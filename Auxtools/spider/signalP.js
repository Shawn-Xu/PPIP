var casper = require('casper').create({
        // used in release
		verbose: false,
        logLevel: "info",
		//used in development
        verbose: true,
        logLevel: "debug"
});

var fs = require('fs');
//var fname = 'signalP_result.txt';
//var save = fs.pathJoin(fs.workingDirectory, fname);


casper.echo("Casper CLI passed options:");
require("utils").dump(casper.cli.options);

casper.start('http://www.cbs.dtu.dk/services/SignalP/', function() {
	casper.log(this.getTitle(),"info");
});

casper.then(function() {
	var minlen=10
	var trunc=70
	var method="best"    //best, notm   (default is best)
	var orgtype="euk"    //euk, gram+, gram-  (default is euk)
	if(casper.cli.get('minlen'))
	{
		minlen=casper.cli.get('minlen') 
	}
	if(casper.cli.get('trunc'))
	{
		trunc=casper.cli.get('trunc') 
	}
	if(casper.cli.get('method'))
	{
		method=casper.cli.get('method') 
	}
	if(casper.cli.get('orgtype'))
	{
		orgtype=casper.cli.get('orgtype') 
	}

	var pars
	if(casper.cli.get('dcut')==="user")
	{
		//console.log("dcut=user")
		var notm=0.45
		var tm=0.5
		if(casper.cli.get('notm'))
		{
			notm=casper.cli.get('notm') 
		}
		if(casper.cli.get('tm'))
		{
			tm=casper.cli.get('tm') 
		}


		pars={
			"SEQSUB": casper.cli.get("fasta"), //
			"method": method,   //best, notm   (default is best)
			"orgtype": orgtype,   //euk, gram+, gram-    (default is euk)
			"format": "short", 
			"minlen": minlen,
			"trunc": trunc,
			"Dcut-type": "user",  //user
			"Dcut-noTM": notm,
			"Dcut-TM": tm
		}
	}
	else
	{
		pars={
			"SEQSUB": casper.cli.get("fasta"), //
			"method": method,   //best, notm   (default is best)
			"orgtype": orgtype,   //euk, gram+, gram-    (default is euk)
			"format": "short", 
			"minlen": minlen,
			"trunc": trunc,
			"Dcut-type": casper.cli.get('Dcut-type')  //default, ver3
		}

	}

	this.fill('form[action="/cgi-bin/webface2.fcgi"]', pars, true);

	this.waitForSelector("pre",
		function pass () {
			casper.log("Got results!","info");
		},
		function fail () {
			casper.log("Failed to load results",'error');
		},
		600000 // timeout limit in milliseconds, this is ten minutes
	);
});
casper.then(function () {
	var save = fs.pathJoin(fs.workingDirectory, "signalP_result.txt");
	if(casper.cli.get('outfile'))
	{
		save=casper.cli.get('outfile') 
	}

	//var htmlToWrite = this.getHTML();
	//fs.write(save, htmlToWrite, "w");
	var result = this.evaluate(function () {
		var pre =  document.querySelector("pre pre").textContent
		return pre;
	});
	
	var news = [];
	news.push(["ID", "Cmax", "Cpos", "Ymax", "Ypos", "Smax", "Spos", "Smean", "D", "isSignal", "Dmaxcut", "Networks-used"].join("\t"))
	var lines = result.split("\n");
	for (i = 0; i < lines.length; i += 1) {
		if(lines[i].substring(0,1)!=="#")  //startsWith is the feature of js ES6. Currently, phantomjs will not support ES5 until phantomjs 2.5
		{
			var elem=lines[i].split(/\s+/)
			if(elem.length>10)
			{
				news.push(elem.join("\t"))
			}
		}
	}
	console.log("###########")
	console.log(save)
	fs.write(save, news.join("\n"), 'w');
});

casper.run();

