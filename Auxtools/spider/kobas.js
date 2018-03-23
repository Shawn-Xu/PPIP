/*
 *selenium框架开发的爬虫个人应用问题不大，但是不方便打包发布，
 *即使用kotlin封装也无法解决这个问题。selenium需要依赖headless浏览器phantomjs,
 *但是无头浏览器应对ajax请求往往力不从心，这时需要有头浏览器支持。所以就需要chromedriver.
 *而且还得安装chrome浏览器，同时还需要X支持，这对docker部署来说极难。
 *而casperjs本质只是个框架，虽然也依赖phantomjs。实现原理也不一样，因此在selenium中
 *需要有头浏览器支持的功能方式， 用casperjs则可以直接实现。
 *再者，casperjs没有selenium退出后会有phantomjs驻留进程不自动退出的问题。
 *综上，casperjs优于selenium。
*/
var casper = require('casper').create({
	// used in release
	verbose: false,
	logLevel: "info",
	//used in development
	verbose: true,
	logLevel: "debug"

});
var fs = require('fs');
//var fname = 'kobas_result.txt';
//var save = fs.pathJoin(fs.workingDirectory, fname);

casper.echo("Casper CLI passed options:");
require("utils").dump(casper.cli.options);

casper.start('http://kobas.cbi.pku.edu.cn/annotate.php', function () {
	casper.log(this.getTitle(),"info");
});

casper.then(function () {
	var orgtype = "Homo sapiens (human)";    //default
	var fa;
	if(casper.cli.get('species'))
	{
		orgtype=casper.cli.get('species')
	}
	if(casper.cli.get('fasta'))
	{
		fa=casper.cli.get('fasta') 
	}
	var pars = {
		"input_type": "fasta:pro",
		"SpeciesSearch": orgtype,
		"KO": false,
		"input_file1": fa
	};

	this.fill('form[action="./wait_annotate.php"]', pars, false);  //第一个参数是css选择器。下面提交，所以第三个参数设为false
	this.evaluate(function () {  //这里不能用fill提交，参考http://blog.csdn.net/duyuanhai/article/details/38023965。我用这种函数来submit。
		document.querySelector('form#form1').submit();
	});
	this.waitForSelector({ type: "xpath", path: "//em[text()='(You can save this link to fetch results directly in the future.)']" },
		//this.waitForSelector("div#table1_length",
		function pass() {
			casper.log("Got results!","info");
		},
		function fail() {
			casper.log("Failed to submit form!", 'error');
		},
		600000 // timeout limit in milliseconds,这里设成10分钟
	);
});
casper.then(function () {
	var save = fs.pathJoin(fs.workingDirectory, "kobas_result.txt");
	if(casper.cli.get('outfile'))
	{
			save=casper.cli.get('outfile')
	}

	var htmlToWrite = this.getHTML();
	var dlUrl = this.evaluate(function () {
		var txt = document.querySelector("#input > p > a").textContent
		return txt;
	});

	//var dlUrl = "http://kobas.cbi.pku.edu.cn/result_annotate.php?taskid=171206506400417";
	var myRegexp = /taskid=(\d+)$/;
	var match = myRegexp.exec(dlUrl);
	if(match === null)
	{
		casper.log('Failed to download result!', 'error');
	}else
	{
		casper.log("The task id is:\n\t"+match[1],"info"); // id
		//casper.download("http://kobas.cbi.pku.edu.cn/download_file.php?type=run_annotate&taskid=" + match[1], fname);
		casper.download("http://kobas.cbi.pku.edu.cn/download_file.php?type=run_annotate&taskid=" + match[1], save);
	}
});

casper.run();
