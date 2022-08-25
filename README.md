# uOpTime

Also called μOpTime

Benutze RMAD als Instabilitätsmaß (oder anderes relatives Streuungsmaß in % des Mittelwerts (mean oder median)).

Grenze zur Instabilität: RMAD > 0.01 (1% des Mittels Abweichung)

Absolute Minimalkonfiguration:
- IR: 2?
- SR: 1
- It: 3
- BED: 1s



stable overall -> reduce ir (how advisable is this, as the randomness comes from the cloud?)
stable within ir -> reduce sr
stable within sr -> reduce iterations
stable within it -> reduce benchtime
