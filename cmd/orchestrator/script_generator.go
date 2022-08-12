package main

import (
	_ "embed"
	"fmt"
)

//go:embed build/runner
var runnerBytes []byte

func generateStartupScript(projUri string, basePackage string, bed string, iterations int, sr int, orchestratorIp string) []byte {
	scriptFormatString := `#!/bin/bash

# define the tasks that need to be done with the extracted content
run_benchmark_runner() {
    cd $WORK_DIR
    chmod +x runner
    git clone %s proj
    ./runner -path $WORK_DIR/proj -base-package %s -bed %s -iterations %d -sr %d -orchestrator-ip %s
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
	return append([]byte(fmt.Sprintf(scriptFormatString, projUri, basePackage, bed, iterations, sr, orchestratorIp)), runnerBytes...)
}
