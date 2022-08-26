package common

import (
	"os/exec"
	"regexp"
	"strings"

	"github.com/pkg/errors"
	benchparser "golang.org/x/tools/benchmark/parse"
)

type (
	Measurement struct {
		N       int
		NsPerOp float64
		BedPos  int
		ItPos   int
		SrPos   int
	}

	Benchmark struct {
		Name        string
		NameRegexp  string
		Package     string
		ProjectPath string
		Measurement []Measurement
	}

	queueElem struct {
		benchmark *Benchmark
		bedSetup  int
		itSetup   int
		srSetup   int
		irSetup   int
		irPos     int
	}
)

var msrmntQueue chan queueElem

// maskNameRegexp turns a benchmark name, e.g., BenchmarkNumberOne/20, into a regular expression,
// which will never accidentally execute other benchmarks.
// For some reason, '/' has a special meaning in "go test -bench x" and the beginning (^) and end ($)
// have to be marked in every substring around a '/'.
//
// Every substring around '/' seems to be treated like its own regular expression. As far as I can tell,
// this behavior is not documented. See https://github.com/golang/go/blob/master/src/testing/match.go at func splitRegexp.
func maskNameRegexp(name string) string {
	nameQuoted := regexp.QuoteMeta(name)
	nameSplit := strings.Split(nameQuoted, "/")
	nameRegexp := ""

	for i := 0; i < len(nameSplit)-1; i++ {
		nameRegexp = nameRegexp + "^" + nameSplit[i] + "$/"
	}
	nameRegexp = nameRegexp + "^" + nameSplit[len(nameSplit)-1] + "$" // last iteration without '/'

	return nameRegexp
}

// CollectBenchmarks runs all benchmarks of the given project, and gathers their names
func CollectBenchmarks(projName string, projPath string, basePackage string) (*[]Benchmark, error) {
	// register project in DB
	insertProject(projName, basePackage)

	// run all benchmarks and get output
	cmd := exec.Command("go", "test", "-benchtime", "1x", "-bench", ".", "./...")
	cmd.Dir = projPath
	out, err := cmd.CombinedOutput()
	if err != nil {
		return nil, errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
	}

	// allocate list for benchmarks
	benchmarks := make([]Benchmark, 0, 10)

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

			benchmarks = append(benchmarks, Benchmark{
				Name:        nameTrimmed,
				NameRegexp:  maskNameRegexp(nameTrimmed), // Name needs special format for execution
				Package:     pkg,
				ProjectPath: projPath,
				Measurement: []Measurement{},
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

func (bench *Benchmark) RunBenchmark(bed int, itPos int, srPos int) error {
	for i := 0; i < bed; i++ { // each iteration on this level is 1s of benchtime, repeat until bed is reached
		cmd := exec.Command("go", "test", "-benchtime", "1s", "-bench", bench.NameRegexp, bench.Package)
		cmd.Dir = bench.ProjectPath
		out, err := cmd.CombinedOutput()
		if err != nil {
			return errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
		}

		// split output into lines
		lines := strings.Split(string(out), "\n")

		// parse output
		for j := 0; j < len(lines); j++ {
			isBench, err := regexp.MatchString("^Benchmark", lines[j])
			if err != nil {
				return errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
			}

			if isBench {
				b, err := benchparser.ParseLine(lines[j])
				if err != nil {
					return errors.Wrapf(err, "%#v: output: %s", cmd.Args, out)
				}

				// save new measurement
				newMsrmnt := Measurement{
					N:       b.N,
					NsPerOp: b.NsPerOp,
					BedPos:  i + 1,
					ItPos:   itPos,
					SrPos:   srPos,
				}

				bench.Measurement = append(bench.Measurement, newMsrmnt)
			}
		}
	}

	return nil
}

func (bench *Benchmark) RecordMeasurement(bedSetup int, itSetup int, srSetup int, irSetup int, irPos int) {
	if msrmntQueue == nil {
		msrmntQueue = make(chan queueElem, 500)
		go dbQueueConsumer()
	}
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

func dbQueueConsumer() {
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
