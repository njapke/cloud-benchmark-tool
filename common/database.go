package common

import (
	"database/sql"
	"errors"
	log "github.com/sirupsen/logrus"
	_ "modernc.org/sqlite"
	"os"
)

type (
	DbConfig struct {
		Type string
		Uri  string
	}
)

var db *sql.DB

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
		"bed" TEXT NOT NULL,
		"iterations" INT NOT NULL,
		"sr" INT NOT NULL,
		"ir" INT NOT NULL,
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

func insertMeasurement(bName string, n int, nsPerOp float64, bed string, iterations int, sr int, ir int) {
	log.Debug("Inserting measurement record ...")
	insertMeasurementSQL := `INSERT INTO measurement(n, ns_per_op, bed, iterations, sr, ir, b_name) VALUES (?, ?, ?, ?, ?, ?, ?)`
	statement, err := db.Prepare(insertMeasurementSQL) // Prepare statement
	// This is good to avoid SQL injections
	if err != nil {
		log.Fatalln(err.Error())
	}
	_, err = statement.Exec(n, nsPerOp, bed, iterations, sr, ir, bName)
	if err != nil {
		log.Fatalln(err.Error())
	}
}
