all: bar.j bar.class

bar.j: *.py
	python3 .

bar.class: bar.j ast.py
	java -jar ~/jasmin-2.4/jasmin.jar *.j

clean:
	rm -f *.j *.class
