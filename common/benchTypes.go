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
)

// MaskNameRegexp turns a benchmark name, e.g., BenchmarkNumberOne/20, into a regular expression,
// which will never accidentally execute other benchmarks.
// For some reason, '/' has a special meaning in "go test -bench x" and the beginning (^) and end ($)
// have to be marked in every substring around a '/'.
//
// Every substring around '/' seems to be treated like its own regular expression. As far as I can tell,
// this behavior is not documented. See https://github.com/golang/go/blob/master/src/testing/match.go at func splitRegexp.
func MaskNameRegexp(name string) string {
	nameQuoted := regexp.QuoteMeta(name)
	nameSplit := strings.Split(nameQuoted, "/")
	nameRegexp := ""

	for i := 0; i < len(nameSplit)-1; i++ {
		nameRegexp = nameRegexp + "^" + nameSplit[i] + "$/"
	}
	nameRegexp = nameRegexp + "^" + nameSplit[len(nameSplit)-1] + "$" // last iteration without '/'

	return nameRegexp
}

func (bench *Benchmark) RunBenchmark(bed int, itPos int, srPos int) error {
	cmd := exec.Command("go", "clean", "--cache")
	//cmd.Dir =
	_, err := cmd.CombinedOutput()
	if err != nil {
		return errors.Wrapf(err, "%#v: error while running go clean --cache.", cmd.Args)
	}

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
