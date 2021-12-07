paida_library = """
/*jslb_ajax050 2.652k @see http://jsgt.org/mt/archives/01/000409.html*/
/*Original by Toshiro Takahashi. Modified by Koji Kishimoto*/

function chkAjaBrowser(){
	var a,ua=navigator.userAgent;
	this.bw={safari:((a=ua.split('AppleWebKit/')[1])?a.split('(')[0]:0)>=124,konqueror:((a=ua.split('Konqueror/')[1])?a.split(';')[0]:0)>=3.3,mozes:((a=ua.split('Gecko/')[1])?a.split(" ")[0]:0)>=20011128,opera:(!!window.opera)&&((typeof XMLHttpRequest)=='function'),msie:(!!window.ActiveXObject)?(!!createHttpRequest()):false};
	return(this.bw.safari || this.bw.konqueror || this.bw.mozes || this.bw.opera || this.bw.msie)
};

function createHttpRequest(){
	if(window.XMLHttpRequest){
		return new XMLHttpRequest();
	}else if(window.ActiveXObject){
		try{
			return new ActiveXObject("Msxml2.XMLHTTP");
		}catch(e){
			try{
				return new ActiveXObject("Microsoft.XMLHTTP");
			}catch(e2){
				return null;
			}
		}
	}else{
		return null;
	}
};

function sendRequest(callback,arg,data,method,url,async,sload,user,password){
	sendRequest.prototype.README={url:"http://jsgt.org/mt/archives/01/000409.html",name:"sendRequest",version:0.50,license:"Public Domain",author:"Toshiro Takahashi http://jsgt.org/mt/01/",memo:""};
	var oj=createHttpRequest();
	if(oj==null){
		return null;
	}
	var sload=(!!sendRequest.arguments[5])?sload:false;
	if(sload || method.toUpperCase()=='GET'){
		url+="?";
	}
	if(sload){
		url=url+"t="+(new Date()).getTime();
	}
	var bwoj=new chkAjaBrowser();
	var opera=bwoj.bw.opera;
	var safari=bwoj.bw.safari;
	var konqueror=bwoj.bw.konqueror;
	var mozes=bwoj.bw.mozes;
	if(typeof callback=='object'){
		var callback_onload=callback.onload;
		var callback_onbeforsetheader=callback.onbeforsetheader
	}else{
		var callback_onload=callback;
		var callback_onbeforsetheader=null;
	};
	if(opera || safari || mozes){
		oj.onload=function(){
			callback_onload(oj,arg);
		}
	}else{
		oj.onreadystatechange=function(){
			if(oj.readyState==4){
				callback_onload(oj,arg);
			}
		}
	};
	data=uriEncode(data,url);
	if(method.toUpperCase()=='GET'){
		url+=data
	};
	oj.open(method,url,async,user,password);
	if(!!callback_onbeforsetheader){
		callback_onbeforsetheader(oj,arg);
	}
	setEncHeader(oj);
	oj.send(data);
	
	function setEncHeader(oj){
		var contentTypeUrlenc='application/x-www-form-urlencoded; charset=UTF-8';
		if(!window.opera){oj.setRequestHeader('Content-Type',contentTypeUrlenc);
		}else{
			if((typeof oj.setRequestHeader)=='function')oj.setRequestHeader('Content-Type',contentTypeUrlenc);
		};
		return oj
	};
	
	function uriEncode(data,url){
		var encdata=(url.indexOf('?')==-1)?'?dmy':'';
		if(typeof data=='object'){
			for(var i in data){
				encdata+='&'+encodeURIComponent(i)+'='+encodeURIComponent(data[i]);
			}
		}else if(typeof data=='string'){
			if(data==""){
				return"";
			}
			var encdata='';
			var datas=data.split('&');
			for(i=1;i<datas.length;i++){
				var dataq=datas[i].split('=');
				encdata+='&'+encodeURIComponent(dataq[0])+'='+encodeURIComponent(dataq[1]);
			}
		};
		return encdata;
	};
	return oj
}


/*PAIDA library*/

function check(id) {
	sendRequest(update, id, '', 'GET', id, true, true);
}

function update(object, id) {
	var response = decodeURIComponent(object.responseText);
	var commands, command;
	var items, item;
	var pair;
	var instance;
	var canvas = document.getElementById("canvas");
	if (response != "") {
		commands = response.split("#");
		for (i = 0; i < commands.length; i++) {
			command = commands[i];
			items = command.split("&");
			for (j = 0; j < items.length; j++) {
				item = items[j];
				if (item != "") {
					pair = item.split("=");
					name = pair[0];
					value = pair[1];
					if (name == "_name_") {
						instance = document.createElementNS("http://www.w3.org/2000/svg", value);
					} else if (name == "_text_") {
						instance = document.createElementNS("http://www.w3.org/2000/svg", "text");
						instance.appendChild(document.createTextNode(value));
					} else {
						if ((name == "fill") && (value == "")) {
							value = "none";
						}
						if (value != "") {
							instance.setAttribute(name, value)
						}
					}
				}
			}
			canvas.appendChild(instance);
		}
	}
	if (id == '/plotter') {
		setTimeout("check('" + id + "')", 300);
	} else if (id == '/tree') {
		setTimeout("check('" + id + "')", 1000)
	}
}
"""