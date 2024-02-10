watch-go: 
	watchexec -e go -r -- go run cmd/main.go

watch-templ: 
	watchexec -e templ -- templ generate

watch: 
	make watch-go & make watch-templ & wait

