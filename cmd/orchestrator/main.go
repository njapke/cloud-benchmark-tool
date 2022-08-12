package main

import (
	compute "cloud.google.com/go/compute/apiv1"
	"cloud.google.com/go/storage"
	"context"
	"encoding/gob"
	"flag"
	"fmt"
	"github.com/BurntSushi/toml"
	log "github.com/sirupsen/logrus"
	"google.golang.org/api/option"
	"io"
	"ma-project/common"
	"net"
	"os/signal"
	"strconv"
	"sync"

	"math/rand"

	"os"
	"time"
)

type (
	config struct {
		Name        string
		Path        string
		ProjUri     string
		BasePackage string
		Bed         string
		Iterations  int
		Sr          int
		Ir          int
	}
	cmdArgs struct {
		CleanDB         bool
		CredentialsFile string
		SqliteFile      string
		Ip              string
		InstanceName    string
	}
	setup struct {
		Bed        string
		Iterations int
		Sr         int
		Ir         int
		Mu         sync.Mutex
	}
)

var wg sync.WaitGroup
var wgIr sync.WaitGroup
var currSetup setup

// TODO config.toml and credentials via arguments
func parseArgs() (ca cmdArgs) {
	flag.BoolVar(&(ca.CleanDB), "clean-db", false, "Clean database, i.e., drop all tables related to benchmark data collection.")
	flag.StringVar(&(ca.CredentialsFile), "credentials-file", "creds.json", "Path to credentials.json for GCP.")
	flag.StringVar(&(ca.SqliteFile), "sqlite-file", "database.db", "Path to sqlite3 database file.")
	flag.StringVar(&(ca.Ip), "ip", "127.0.0.1", "IP address of this node.")
	flag.StringVar(&(ca.InstanceName), "instance-name", "orchestrator", "GCP instance name of the orchestrator, so that it does not shut itself down.")

	flag.Parse()

	// TODO fix multiple slashes in paths

	return
}

func main() {
	// Seed rand with current time (running with no seed gives deterministic results)
	rand.Seed(time.Now().UnixNano())

	// parse cmd arguments
	ca := parseArgs()

	// Initiate logging
	log.SetOutput(os.Stdout)
	log.SetLevel(log.DebugLevel)

	log.Debugln("Reading config")

	f := "config.toml"
	var cfg config

	_, err := toml.DecodeFile(f, &cfg)

	if err != nil {
		log.Errorln(err)
		panic(err)
	}

	log.Debugln("Finished reading config")
	log.Debugln(cfg)

	// TODO: write to and read from DB
	// --- Connect to DB (sqlite) ---
	common.ConnectToDB(common.DbConfig{
		Type: "sqlite",
		Uri:  ca.SqliteFile,
	}, ca.CleanDB) // assigns the global variable db
	defer common.CloseDB() // Defer Closing the database
	// --- Finish connect to DB ---

	// TODO: read benchmarks from db, if no forced reread or db clean
	log.Debugf("Begin collecting benchmarks of %s", cfg.Name)
	benchmarks, err := common.CollectBenchmarks(cfg.Name, cfg.Path, cfg.BasePackage)
	if err != nil {
		log.Fatalln(err)
	}
	log.Debugf("Finished collecting benchmarks of %s", cfg.Name)
	log.Debugf("Found benchmarks: %+v", *benchmarks)

	// Start server endpoints

	// Sending benchmarks
	quitSend := make(chan bool, 1)
	inSend, err := net.Listen("tcp", ":5000")
	if err != nil {
		log.Fatalln(err)
	}
	go sendBenchmarkHandler(benchmarks, &inSend, quitSend)

	// Sending benchmarks
	quitRecv := make(chan bool, 1)
	inRecv, err := net.Listen("tcp", ":5001")
	if err != nil {
		log.Fatalln(err)
	}
	go readMeasurementHandler(&inRecv, quitRecv)

	// GCP STUFF
	ctx := context.Background()
	creds := option.WithCredentialsFile(ca.CredentialsFile)

	// open gcp clients
	gclientStorage, err := storage.NewClient(ctx, creds)
	if err != nil {
		log.Fatalln(err)
	}
	defer gclientStorage.Close()
	gclientCompute, err := compute.NewInstancesRESTClient(ctx, creds)
	if err != nil {
		log.Fatalln(err)
	}
	defer gclientCompute.Close()

	// start setup
	currSetup.Mu.Lock()
	currSetup.Bed = "1s"
	currSetup.Iterations = 1
	currSetup.Sr = 1
	currSetup.Ir = cfg.Ir
	currSetup.Mu.Unlock()

	for i := 0; i < 75; i++ {
		// TODO temporary emission of startup script; works perfectly in tests
		currSetup.Mu.Lock()
		script := generateStartupScript(cfg.ProjUri, cfg.BasePackage, currSetup.Bed, currSetup.Iterations, currSetup.Sr, ca.Ip)
		instances := currSetup.Ir
		log.Debugf("Test No %d\nSetup: BED = %s, It = %d, SR = %d, IR = %d", i, currSetup.Bed, currSetup.Iterations, currSetup.Sr, currSetup.Ir)
		currSetup.Mu.Unlock()
		/*fT, _ := os.Create("tmp")
		fT.Write(script)
		fT.Chmod(0777)
		fT.Close()*/

		// upload startup script
		uploadBytes(script, ca.InstanceName, gclientStorage, ctx)

		listOfInstances := make([]string, 3)

		for j := 0; j < instances; j++ {
			name := fmt.Sprintf("%s-instance-%d", ca.InstanceName, j)
			createInstance(name, ca.InstanceName, gclientCompute, ctx)
			listOfInstances = append(listOfInstances, name)
			wgIr.Add(1)
		}
		log.Debugln(listOfInstances)

		// wait for results
		wgIr.Wait()
		// shutdown instances
		shutdownAllInstances(&listOfInstances, gclientCompute, ctx)

		// get next setup
		nextSetup()
	}

	log.Debugln("Finished experiment")

	// Only end when Crtl+C is pressed
	c := make(chan os.Signal, 1)   // create channel on os.Signal
	signal.Notify(c, os.Interrupt) // notify channel on Crtl+C
	for sig := range c {           // wait and block until notify
		fmt.Println(sig.String())
		quitSend <- true
		quitRecv <- true
		break // break and end program after notify
	}
	inSend.Close()
	inRecv.Close()
	wg.Wait()
	close(quitSend)
	close(quitRecv)
	close(c)
}

func sendBenchmarks(benchmarks *[]common.Benchmark, conn net.Conn) {
	wg.Add(1)
	defer wg.Done()
	encoder := gob.NewEncoder(conn)
	N := len(*benchmarks)
	log.Debugln("Sending benchmarks to instance")
	for i := 0; i < N; i++ {
		encoder.Encode((*benchmarks)[i])
	}
	conn.Close()
	log.Debugln("Finished sending benchmarks")
}

func sendBenchmarkHandler(benchmarks *[]common.Benchmark, in *net.Listener, quit <-chan bool) {
Loop:
	for {
		select {
		case <-quit:
			break Loop // Break out of loop
		default:
			conn, err := (*in).Accept()
			if err != nil {
				log.Errorln(err)
				continue
			}
			go sendBenchmarks(benchmarks, conn)
		}
	}
}

func readMeasurements(conn net.Conn) {
	//wg.Add(1)
	//defer wg.Done()
	defer wgIr.Done() // TODO: unsafe, can be tampered with, maybe not important?

	benchmarks := make([]common.Benchmark, 0, 10)

	dec := gob.NewDecoder(conn)
	log.Debugln("Receiving measurements from instance")
	for {
		var b common.Benchmark
		err := dec.Decode(&b)
		if err != nil {
			if err == io.EOF {
				break
			} else {
				log.Fatalln(err)
			}
		}

		benchmarks = append(benchmarks, b)
	}
	log.Debugln("Finished receiving measurements")

	// record measurements in db
	currSetup.Mu.Lock()
	bed := currSetup.Bed
	iterations := currSetup.Iterations
	sr := currSetup.Sr
	ir := currSetup.Ir
	currSetup.Mu.Unlock()

	for i := 0; i < len(benchmarks); i++ {
		benchmarks[i].RecordMeasurement(bed, iterations, sr, ir)
	}
	log.Debugln("Finished writing measurements into db")
}

func readMeasurementHandler(in *net.Listener, quit <-chan bool) {
Loop:
	for {
		select {
		case <-quit:
			break Loop // Break out of loop
		default:
			conn, err := (*in).Accept()
			if err != nil {
				log.Errorln(err)
				continue
			}
			go readMeasurements(conn)
		}
	}
}

func nextSetup() {
	bedInt, _ := strconv.Atoi(currSetup.Bed[:1])

	currSetup.Mu.Lock()
	bedInt += 1
	if bedInt > 5 {
		bedInt = 1
		currSetup.Iterations += 1
		if currSetup.Iterations > 5 {
			currSetup.Iterations = 1
			currSetup.Sr += 1
			if currSetup.Sr > 3 {
				currSetup.Sr = 1
			}
		}
	}
	currSetup.Bed = strconv.Itoa(bedInt) + "s"
	currSetup.Mu.Unlock()
}
