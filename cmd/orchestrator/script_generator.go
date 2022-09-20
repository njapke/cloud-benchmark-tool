package main

import (
	_ "embed"
	"fmt"
)

//go:embed build/runner
var runnerBytes []byte

func generateStartupScript(projUri string, tag string, basePackage string, bed int, iterations int, sr int, orchestratorIp string, benchListPort string, msrmntReportPort string) []byte {
	scriptFormatString := `#!/bin/bash

# define the tasks that need to be done with the extracted content
run_benchmark_runner() {
    cd $WORK_DIR
    chmod +x runner
    git clone %s proj
	cd proj
	git fetch --all --tags
	git checkout tags/%s
	cd ..
    ./runner -path $WORK_DIR/proj -base-package %s -bed %d -iterations %d -sr %d -orchestrator-ip %s -benchmark-list-port %s -measurement-report-port %s
    # do something with the extracted content
}

WORK_DIR=/tmp
export HOME=/tmp

# line number where payload starts
PAYLOAD_LINE=$(awk '/^__PAYLOAD_BEGINS__/ { print NR + 1; exit 0; }' $0)

# extract the embedded file
tail -n +${PAYLOAD_LINE} $0 >> $WORK_DIR/runner

# perform actions with the extracted content
run_benchmark_runner

exit 0
__PAYLOAD_BEGINS__
`
	return append([]byte(fmt.Sprintf(scriptFormatString, projUri, tag, basePackage, bed, iterations, sr, orchestratorIp, benchListPort, msrmntReportPort)), runnerBytes...)
}
