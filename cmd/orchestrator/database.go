package main

import (
	"cloud-benchmark-tool/common"
	"database/sql"
	"github.com/pkg/errors"
	log "github.com/sirupsen/logrus"
	benchparser "golang.org/x/tools/benchmark/parse"
	_ "modernc.org/sqlite"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"sync"
)

type (
	DbConfig struct {
		Type string
		Uri  string
	}

	queueElem struct {
		benchmark *common.Benchmark
		bedSetup  int
		itSetup   int
		srSetup   int
		irSetup   int
		irPos     int
	}
)

var db *sql.DB
var msrmntQueue chan queueElem
var queueMu sync.Mutex

// ConnectToDB creates a database connection.
// dbConfig contains information on the type of database and location
// cleanDb instructs the dropping of all relevant tables
func ConnectToDB(dbConfig DbConfig, cleanDb bool) { // TODO finish
	connectToSqlite()

	initializeDB(cleanDb)
}

// TODO: Finish (does not clean up or handle existing DB)
// TODO: error handling
func connectToSqlite() {
	if _, err := os.Stat("sqlite-database.db"); errors.Is(err, os.ErrNotExist) {
		log.Debug("Creating sqlite-database.db")
		file, err := os.Create("sqlite-database.db") // Create SQLite file
		if err != nil {
			log.Fatal(err.Error())
		}
		file.Close()
		log.Debug("sqlite-database.db created")
	}

	log.Debug("Connecting to sqlite-database.db")
	sqliteDatabase, _ := sql.Open("sqlite", "./sqlite-database.db") // Open the created SQLite File
	db = sqliteDatabase                                             // save in global variable
	log.Debug("Finished connecting to sqlite-database.db")
}

func CloseDB() {
	db.Close()
}

// CollectBenchmarks runs all benchmarks of the given project, and gathers their names
func CollectBenchmarks(projName string, projPath string, basePackage string) (*[]common.Benchmark, error) {
	// register project in DB
	insertProject(projName, basePackage)

	// run all benchmarks and get output
	cmd := exec.Command("go", "test", "-timeout", "0", "-benchtime", "1x", "-bench", ".", "./...")
	cmd.Dir = projPath
	out, err := cmd.CombinedOutput()
	if err != nil {
		if exiterr, ok := err.(*exec.ExitError); ok {
			log.Debugf("Exit Status: %d", exiterr.ExitCode())
		} else {
			return nil, errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
		}
	}

	// allocate list for benchmarks
	benchmarks := make([]common.Benchmark, 0, 10)

	// split output into lines
	lines := strings.Split(string(out), "\n")

	// default package
	pkg := "./"

	// parse output from go test
	for i := 0; i < len(lines); i++ {
		isBench, err := regexp.MatchString("^Benchmark", lines[i])
		if err != nil {
			return nil, errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
		}

		if isBench {
			b, err := benchparser.ParseLine(lines[i])
			if err != nil {
				return nil, errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
			}

			// go test appends -#cpu to every name, and the parser does not remove this suffix
			// since go test does not consider the suffix part of the name, it has to be removed
			nameSplit := strings.Split(b.Name, "-")               // split at -
			nameSuffix := "-" + nameSplit[len(nameSplit)-1]       // get last position (number of cpus used in run)
			nameTrimmed := strings.TrimSuffix(b.Name, nameSuffix) // remove suffix

			benchmarks = append(benchmarks, common.Benchmark{
				Name:        nameTrimmed,
				NameRegexp:  common.MaskNameRegexp(nameTrimmed), // Name needs special format for execution
				Package:     pkg,
				ProjectPath: projPath,
				Measurement: []common.Measurement{},
			})

			// TODO: register benchmark in DB
			insertBenchmark(nameTrimmed, pkg, projName)

			continue // go to next iteration
		}

		isPkg, err := regexp.MatchString("^pkg:", lines[i])
		if err != nil {
			return nil, errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
		}

		if isPkg {
			_, after, found := strings.Cut(strings.Fields(lines[i])[1], basePackage)
			if !found {
				return nil, errors.New("Base package not found in subpackage string. Maybe misconfigured?")
			}
			if strings.HasPrefix(after, "/") {
				after = "." + after
			} else {
				after = "./" + after
			}
			pkg = after
		} // discard no match
	}
	return &benchmarks, nil
}

// initializeDB ensures that the necessary tables are created. If cleanDb is true, the tables are emptied
// by running drop statements as well.
func initializeDB(cleanDb bool) {
	// --- clean DB ---
	if cleanDb {
		// --- drop project table ---
		dropProjectTableSQL := `DROP TABLE IF EXISTS project;`

		log.Debug("Drop project table")
		dropProjectStatement, err := db.Prepare(dropProjectTableSQL) // Prepare SQL Statement
		if err != nil {
			log.Fatal(err.Error())
		}
		dropProjectStatement.Exec() // Execute SQL Statements
		log.Debug("project table dropped")

		// --- drop benchmark table ---
		dropBenchmarkTableSQL := `DROP TABLE IF EXISTS benchmark;`

		log.Debug("Drop benchmark table")
		dropBenchmarkStatement, err := db.Prepare(dropBenchmarkTableSQL) // Prepare SQL Statement
		if err != nil {
			log.Fatal(err.Error())
		}
		dropBenchmarkStatement.Exec() // Execute SQL Statements
		log.Debug("benchmark table dropped")

		// --- drop measurement table ---
		dropMeasurementTableSQL := `DROP TABLE IF EXISTS measurement;`

		log.Debug("Drop measurement table")
		dropMeasurementStatement, err := db.Prepare(dropMeasurementTableSQL) // Prepare SQL Statement
		if err != nil {
			log.Fatal(err.Error())
		}
		dropMeasurementStatement.Exec() // Execute SQL Statements
		log.Debug("measurement table dropped")
	}

	// --- create project table ---
	createProjectTableSQL := `CREATE TABLE IF NOT EXISTS project (
		"p_name" TEXT NOT NULL PRIMARY KEY,
		"base_package" TEXT NOT NULL
	  );`

	log.Debug("Create project table")
	createProjectStatement, err := db.Prepare(createProjectTableSQL) // Prepare SQL Statement
	if err != nil {
		log.Fatal(err.Error())
	}
	createProjectStatement.Exec() // Execute SQL Statements
	log.Debug("project table created")

	// --- create benchmark table ---
	createBenchmarkTableSQL := `CREATE TABLE IF NOT EXISTS benchmark (
		"b_name" TEXT NOT NULL,
		"subpackage" TEXT NOT NULL,
		"p_name" TEXT NOT NULL,
		FOREIGN KEY(p_name) REFERENCES project(p_name),
		CONSTRAINT PK_Bench PRIMARY KEY (b_name,subpackage,p_name)
	  );`

	log.Debug("Create benchmark table")
	createBenchmarkStatement, err := db.Prepare(createBenchmarkTableSQL) // Prepare SQL Statement
	if err != nil {
		log.Fatal(err.Error())
	}
	createBenchmarkStatement.Exec() // Execute SQL Statements
	log.Debug("benchmark table created")

	// --- create measurement table ---
	createMeasurementTableSQL := `CREATE TABLE IF NOT EXISTS measurement (
    	"m_id" INTEGER PRIMARY KEY AUTOINCREMENT,
		"n" INT NOT NULL,
		"ns_per_op" FLOAT NOT NULL,
		"bed_setup" INT NOT NULL,
		"it_setup" INT NOT NULL,
		"sr_setup" INT NOT NULL,
		"ir_setup" INT NOT NULL,
		"bed_pos" INT NOT NULL,
		"it_pos" INT NOT NULL,
		"sr_pos" INT NOT NULL,
		"ir_pos" INT NOT NULL,
		"b_name" TEXT NOT NULL,
		FOREIGN KEY(b_name) REFERENCES benchmark(b_name)
	  );`

	log.Debug("Create measurement table")
	createMeasurementStatement, err := db.Prepare(createMeasurementTableSQL) // Prepare SQL Statement
	if err != nil {
		log.Fatal(err.Error())
	}
	res, err := createMeasurementStatement.Exec() // Execute SQL Statements
	log.Debugln(res)
	if err != nil {
		log.Fatal(err.Error())
	}
	log.Debug("measurement table created")
}

func insertProject(pName string, basePackage string) {
	log.Debug("Inserting project record ...")
	insertProjectSQL := `INSERT INTO project(p_name, base_package) VALUES (?, ?)`
	statement, err := db.Prepare(insertProjectSQL) // Prepare statement
	// This is good to avoid SQL injections
	if err != nil {
		log.Fatalln(err.Error())
	}
	_, err = statement.Exec(pName, basePackage)
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func insertBenchmark(bName string, subPackage string, pName string) {
	log.Debug("Inserting benchmark record ...")
	insertBenchmarkSQL := `INSERT INTO benchmark(b_name, subpackage, p_name) VALUES (?, ?, ?)`
	statement, err := db.Prepare(insertBenchmarkSQL) // Prepare statement
	// This is good to avoid SQL injections
	if err != nil {
		log.Fatalln(err.Error())
	}
	_, err = statement.Exec(bName, subPackage, pName)
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func insertMeasurement(bName string, n int, nsPerOp float64, bedSetup int, itSetup int, srSetup int, irSetup int, bedPos int, itPos int, srPos int, irPos int) {
	log.Debug("Inserting measurement record ...")
	insertMeasurementSQL := `INSERT INTO measurement(n, ns_per_op, bed_setup, it_setup, sr_setup, ir_setup, bed_pos, it_pos, sr_pos, ir_pos, b_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
	statement, err := db.Prepare(insertMeasurementSQL) // Prepare statement
	// This is good to avoid SQL injections
	if err != nil {
		log.Fatalln(err.Error())
	}
	_, err = statement.Exec(n, nsPerOp, bedSetup, itSetup, srSetup, irSetup, bedPos, itPos, srPos, irPos, bName)
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func RecordMeasurement(bench *common.Benchmark, bedSetup int, itSetup int, srSetup int, irSetup int, irPos int, wg *sync.WaitGroup) {
	queueMu.Lock()
	if msrmntQueue == nil {
		msrmntQueue = make(chan queueElem, 500)
		go dbQueueConsumer(wg)
	}
	queueMu.Unlock()
	currMsrmnt := queueElem{
		benchmark: bench,
		bedSetup:  bedSetup,
		itSetup:   itSetup,
		srSetup:   srSetup,
		irSetup:   irSetup,
		irPos:     irPos,
	}
	msrmntQueue <- currMsrmnt
}

func CloseMeasurementQueue() {
	close(msrmntQueue)
}

func dbQueueConsumer(wg *sync.WaitGroup) {
	wg.Add(1)
	defer wg.Done()
	for {
		elem, more := <-msrmntQueue
		if !more {
			return
		}
		for i := 0; i < len(elem.benchmark.Measurement); i++ {
			currMsrmnt := elem.benchmark.Measurement[i]
			insertMeasurement(elem.benchmark.Name, currMsrmnt.N, currMsrmnt.NsPerOp, elem.bedSetup, elem.itSetup, elem.srSetup, elem.irSetup, currMsrmnt.BedPos, currMsrmnt.ItPos, currMsrmnt.SrPos, elem.irPos)
		}
	}
}
