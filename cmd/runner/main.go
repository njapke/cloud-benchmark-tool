package main

import (
	"encoding/gob"
	"flag"
	"fmt"
	log "github.com/sirupsen/logrus"
	"io"
	"ma-project/common"
	"math/rand"
	"net"
	"regexp"

	"os"
	"time"
)

type (
	cmdArgs struct {
		Path           string
		BasePackage    string
		Bed            string
		Iterations     int
		Sr             int
		OrchestratorIp string
	}
)

func parseArgs() (ca cmdArgs) {
	flag.StringVar(&(ca.Path), "path", "", "Path of the project under test to benchmark.") // Project is cloned by startup script and path passed here
	flag.StringVar(&(ca.BasePackage), "base-package", "", "Base package name used for golang imports.")
	flag.StringVar(&(ca.Bed), "bed", "1s", "Benchmark Execution Duration.")
	flag.IntVar(&(ca.Iterations), "iterations", 1, "Number of iterations for a benchmark.")
	flag.IntVar(&(ca.Sr), "sr", 1, "Number of suite runs for the whole benchmark suite.")

	flag.StringVar(&(ca.OrchestratorIp), "orchestrator-ip", "127.0.0.1", "IP address of the orchestrator program to report results to.")

	flag.Parse()

	// Fix multiple slashes in path
	re := regexp.MustCompile(`/+`)
	ca.Path = re.ReplaceAllString(ca.Path, "/")

	return
}

func main() {
	// Seed rand with current time (running with no seed gives deterministic results)
	rand.Seed(time.Now().UnixNano())

	// parse cmd arguments
	ca := parseArgs()

	// Create log file
	f, err := os.OpenFile("./log.txt", os.O_WRONLY|os.O_CREATE, 0755)
	if err != nil {
		panic(1)
	}

	// Initiate logging
	//log.SetOutput(os.Stdout)
	log.SetOutput(f)
	log.SetLevel(log.DebugLevel)

	// Receive benchmarks from orchestrator
	log.Debugln("Reading benchmarks from orchestrator")
	benchmarks := readBenchmarks(ca.OrchestratorIp, ca.Path)
	log.Debugln(benchmarks)
	log.Debugln("Finished reading benchmarks")

	// Run benchmarks
	for i := 1; i <= ca.Sr; i++ {
		log.Debugf("Begin Suite Run %d of %d", i, ca.Sr)
		order := *common.CreateExtendedPerm(len(*benchmarks), ca.Iterations)
		log.Debugf("Order of this run: %v", order)
		for j := 0; j < len(order); j++ {
			curr := order[j]
			// execute current benchmark
			log.Debugf("Executing %s", (*benchmarks)[curr].Name)
			err := (*benchmarks)[curr].RunBenchmark(ca.Bed)
			if err != nil {
				log.Errorln(err)
				panic(err)
			}
		}
		log.Debugf("Finished Suite Run %d of %d", i, ca.Sr)
	}
	fmt.Printf("%+v\n", benchmarks)

	// Send benchmarks with measurement results back
	log.Debugln("Sending measurements to orchestrator")
	sendMeasurements(benchmarks, ca.OrchestratorIp)
	log.Debugln("Finished sending measurements")
}

func readBenchmarks(ip string, projPath string) *[]common.Benchmark {
	benchmarks := make([]common.Benchmark, 0, 10)

	conn, err := net.Dial("tcp", ip+":5000")
	if err != nil {
		log.Fatalln(err)
	}
	dec := gob.NewDecoder(conn)
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
		// Rewrite project path
		b.ProjectPath = projPath

		benchmarks = append(benchmarks, b)
	}

	return &benchmarks
}

func sendMeasurements(benchmarks *[]common.Benchmark, ip string) {
	conn, err := net.Dial("tcp", ip+":5001")
	if err != nil {
		log.Fatalln(err)
	}
	encoder := gob.NewEncoder(conn)
	N := len(*benchmarks)
	for i := 0; i < N; i++ {
		encoder.Encode((*benchmarks)[i])
	}
	conn.Close()
}
