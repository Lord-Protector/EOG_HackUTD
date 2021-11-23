const http=require('http')
const fs=require('fs')
let atad
let l
http.createServer(function(req,res){
	if (req.url==='/data.json'){
		fs.readFile('data.json',function(err,data){
			atad=data
			l=atad.length
		})
		fs.readFile('pichat.png','base64',function(err,data){
			res.writeHead(200,{'Content-Type':'text/html'})
			res.write(l.toString()+atad+data)
			res.end()
		})
	}else{
		fs.readFile('index.html',function(err,data){
			res.writeHead(200,{'Content-Type':'text/html'})
			res.write(data)
			return res.end()
		})
	}
}).listen(8080)