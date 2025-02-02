﻿/****************************************************************
 *																*		
 * 						      代码库							*
 *                        www.dmaku.com							*
 *       		  努力创建完善、持续更新插件以及模板			*
 * 																*
****************************************************************/
$(document).ready(function() {
		var canvas = document.getElementById("c");
		var ctx = canvas.getContext("2d");
		var c = $("#c");
		var x,y,w,h,cx,cy,l;
		var y = [];
		var b = {
			n:100,
			c:false,    //  颜色  如果是false 则是随机渐变颜色
			bc:'rgba(255,255,255,0.05)',   //  背景颜色
			r:0.9, 
			o:0.05,
			a:1,
			s:20,
		}
		var bx = 0,by = 0,vx = 0,vy = 0;
		var td = 0;
		var p = 0;
		var hs = 0;
		re();
		var color,color2;
		if(b.c){
			color2 = b.c;
		}else{
			color = Math.random()*360;
		}
		
		$(window).resize(function(){
			re();
		});
		var tp1=true,tp2 = false,tp3 = false,tp4 = false,tp5 = false,tp6 = false,tp7 = false,tp8 = false,tp9 = false,tp0 = false;
		function begin(){
			if(tp1){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 1;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				for(var i=0;i<y.length;i++){
					ctx.globalAlpha = y[i].o;
					ctx.fillStyle = color2;
					ctx.beginPath();
					ctx.arc(y[i].x,y[i].y,y[i].r,0,Math.PI*2);
					ctx.closePath();
					ctx.fill();
					y[i].r+=b.r;
					y[i].o-=b.o;
					if(y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}else if(tp2){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 1;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				for(var i=0;i<y.length;i++){
					ctx.globalAlpha = y[i].o;
					ctx.fillStyle = color2;
					ctx.beginPath();
					y[i].r=10;
					ctx.shadowBlur=20;
					ctx.shadowColor=color2;
					ctx.arc(y[i].x,y[i].y,y[i].r,0,Math.PI*2);
					ctx.closePath();
					ctx.fill();
					ctx.shadowBlur=0;
					y[i].o-=b.o;
					y[i].v+=b.a;
					y[i].y+=y[i].v;
					if(y[i].y>=h+y[i].r || y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}else if(tp3){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				td+=5;
				ctx.globalAlpha = 1;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				for(var i=0;i<y.length;i++){
					ctx.globalAlpha = y[i].o;
					ctx.fillStyle = color2;
					ctx.beginPath();
					ctx.shadowBlur=20;
					ctx.shadowColor=color2;
					y[i].r=(1-(y[i].y/h))*20;
					ctx.arc(y[i].x,y[i].y,y[i].r,0,Math.PI*2);
					ctx.closePath();
					ctx.fill();
					ctx.shadowBlur=0;
					y[i].o=y[i].y/h;
					y[i].v+=b.a;
					y[i].y-=b.s;
					y[i].x+=(Math.cos((y[i].y+td)/100)*10);
					if(y[i].y<=0-y[i].r || y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}else if(tp4){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 1;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				for(var i=0;i<y.length;i++){
					ctx.globalAlpha = y[i].o;
					ctx.fillStyle = color2;
					ctx.beginPath();
					ctx.shadowBlur=20;
					ctx.shadowColor=color2;
					y[i].vx2 += (cx - y[i].wx)/1000;
					y[i].vy2 += (cy - y[i].wy)/1000;
					y[i].wx+=y[i].vx2;
					y[i].wy+=y[i].vy2;
					y[i].o-=b.o/2;
					y[i].r=10;
					ctx.arc(y[i].wx,y[i].wy,y[i].r,0,Math.PI*2);
					ctx.closePath();
					ctx.fill();
					ctx.shadowBlur=0;
					if(y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}else if(tp5){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = .18;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				p+=5;
				ctx.globalAlpha = 1;
				ctx.fillStyle = color2;
				ctx.beginPath();
				ctx.shadowBlur=20;
				ctx.shadowColor=color2;
				ctx.arc(cx+50*Math.cos(p*Math.PI/180),cy+50*Math.sin(p*Math.PI/180),10,0,Math.PI*2);
				ctx.closePath();
				ctx.fill();
				ctx.beginPath();
				ctx.arc(cx+50*Math.cos((p+180)*Math.PI/180),cy+50*Math.sin((p+180)*Math.PI/180),10,0,Math.PI*2);
				ctx.closePath();
				ctx.fill();
				ctx.beginPath();
				ctx.arc(cx+50*Math.cos((p+90)*Math.PI/180),cy+50*Math.sin((p+90)*Math.PI/180),10,0,Math.PI*2);
				ctx.closePath();
				ctx.fill();
				ctx.beginPath();
				ctx.arc(cx+50*Math.cos((p+270)*Math.PI/180),cy+50*Math.sin((p+270)*Math.PI/180),10,0,Math.PI*2);
				ctx.closePath();
				ctx.fill();
				ctx.shadowBlur=0;
			}else if(tp6){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 0.2;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				for(var i=0;i<y.length;i++){
					ctx.globalAlpha = y[i].o;
					ctx.strokeStyle = color2;
					ctx.beginPath();
					ctx.lineWidth = 2;
					ctx.moveTo(y[i].x,y[i].y);
					ctx.lineTo((y[i].wx+y[i].x)/2+Math.random()*20,(y[i].wy+y[i].y)/2+Math.random()*20);
					ctx.lineTo(y[i].wx,y[i].wy);
					ctx.closePath();
					ctx.stroke();
					y[i].o-=b.o;
					if(y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}else if(tp7){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 0.2;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				if(y.length<b.n*2){
					hs = Math.random()*2*Math.PI;
					y.push({x:cx+((Math.random()-.5)*100*Math.cos(hs)),y:cy+((Math.random()-.5)*100*Math.cos(hs)),o:1,h:hs});
				}
				for(var i=0;i<y.length;i++){
					ctx.globalAlpha = y[i].o;
					ctx.fillStyle = color2;
					ctx.beginPath();
					y[i].x+=(cx-y[i].x)/10;
					y[i].y+=(cy-y[i].y)/10;
					ctx.arc(y[i].x,y[i].y,1,0,Math.PI*2);
					ctx.closePath();
					ctx.fill();
					y[i].o-=b.o;
					if(y[i].o<=0){
						y[i].h = Math.random()*2*Math.PI;
						y[i].x = cx+((Math.random()-.5)*100*Math.cos(y[i].h));
						y[i].y = cy+((Math.random()-.5)*100*Math.sin(y[i].h));
						y[i].o = 1;
					};
				}
			}else if(tp8){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 0.2;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				ctx.fillStyle = color2;
				if(cx%4 == 0){
					cx+=1;
				}else if(cx%4 == 2){
					cx-=1
				}
				else if(cx%4 == 3){
					cx-=2
				}
				if(cy%4 == 0){
					cy+=1;
				}else if(cy%4 == 2){
					cy-=1
				}
				else if(cy%4 == 3){
					cy-=2
				}
				for(var i=cx-60;i<cx+60;i+=4){
					for(var j=cy-60;j<cy+60;j+=4){
						if(Math.sqrt(Math.pow(cx-i,2)+Math.pow(cy-j,2))<=60){
							ctx.globalAlpha = 1-(Math.sqrt(Math.pow(cx-i,2)+Math.pow(cy-j,2))/60);
							if(Math.random()<.2){
								ctx.fillRect(i,j,3,3);
							}
						}
					}
				}
			}else if(tp9){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 0.2;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				ctx.fillStyle = color2;
				if(cx%4 == 0){
					cx+=1;
				}else if(cx%4 == 2){
					cx-=1
				}
				else if(cx%4 == 3){
					cx-=2
				}
				if(cy%4 == 0){
					cy+=1;
				}else if(cy%4 == 2){
					cy-=1
				}
				else if(cy%4 == 3){
					cy-=2
				}
				if(y.length<b.n){
					y.push({x:cx,y:cy,xv:0,yv:0,o:1});
				}
				for(var i=0;i<y.length;i++){
					if(y[i].xv==0 && y[i].yv==0){
						if(Math.random()<.5){
							if(Math.random()<.5){
								y[i].xv = 3;
							}else{
								y[i].xv = -3;
							}
						}else{
							if(Math.random()<.5){
								y[i].yv = 3;
							}else{
								y[i].yv = -3;
							}
						}
					}else{
						if(y[i].xv == 0){
							if(Math.random()<.66){
								y[i].yv = 0;
								if(Math.random()<.5){
									y[i].xv = 3;
								}else{
									y[i].xv = -3;
								}
							}
						}else if(y[i].yv == 0){
							if(Math.random()<.66){
								y[i].xv = 0;
								if(Math.random()<.5){
									y[i].yv = 3;
								}else{
									y[i].yv = -3;
								}
							}
						}
					}
					y[i].o-=b.o/2;
					ctx.globalAlpha = y[i].o;
					y[i].x+=y[i].xv;
					y[i].y+=y[i].yv;
					ctx.fillRect(y[i].x,y[i].y,3,3);
					if(y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}else if(tp0){
				if(!b.c){
					color+=.1;
					color2 = 'hsl('+color+',100%,80%)';
				}
				ctx.globalAlpha = 0.2;
				ctx.fillStyle = b.bc;
				ctx.fillRect(0,0,w,h);
				ctx.fillStyle = color2;
				y.push({x:cx,y:cy,xv:2,yv:1,o:1});

				for(var i=0;i<y.length;i++){
					y[i].o-=b.o/10;
					ctx.globalAlpha = y[i].o;
					y[i].x+=(Math.random()-.5)*4;
					y[i].y-=1;
					ctx.fillRect(y[i].x,y[i].y,2,2);
					if(y[i].o<=0){
						y.splice(i,1);
						i--;
					};
				}
			}
			window.requestAnimationFrame(begin);
		}
		function re(){
			w = window.innerWidth;
			h = window.innerHeight;
			canvas.width = w;
			canvas.height = h;
			cx = w/2;
			cy = h/2;
		};
		c.mousemove(function(e){
			cx = e.pageX-c.offset().left;
			cy = e.pageY-c.offset().top;
			if(tp4){
				if(Math.random()<=.5){
					if(Math.random()<=.5){
						bx = -10;
					}else{
						bx = w+10;
					}
					by = Math.random()*h;
				}else{
					if(Math.random()<=.5){
						by = -10;
					}else{
						by = h+10;
					}
					bx = Math.random()*w;
				}
				vx = (Math.random()-.5)*8;
				vy = (Math.random()-.5)*8;
			}
			if(tp1 || tp2 || tp3){
				y.push({x:cx,y:cy,r:b.r,o:1,v:0});
			}else if(tp4){
				y.push({x:cx,y:cy,r:b.r,o:1,v:0,wx:bx,wy:by,vx2:vx,vy2:vy});
			}else if(tp6){
				y.push({x:cx+((Math.random()-.5)*30),y:cy+((Math.random()-.5)*30),o:1,wx:cx,wy:cy});
			}
		});
		/*c.mousedown(function(){
			c.on('mousemove',function(e){
				cx = e.pageX-c.offset().left;
				cy = e.pageY-c.offset().top;
				y.push({x:cx,y:cy,r:b.r,o:1});
			});
			c.on('mouseup',function(){
				c.off('mouseup');
				c.off('mousemove');
				c.off('moseleave');
			});
			c.on('mouseleave',function(){
				c.off('mouseup');
				c.off('mousemove');
				c.off('moseleave');
			});
		});*/
		$("#btn1").click(function(){
			tp1 = true;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn2").click(function(){
			tp1 = false;
			tp2 = true;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn3").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = true;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn4").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = true;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn5").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = true;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn6").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = true;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn7").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = true;
			tp8 = false;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn8").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = true;
			tp9 = false;
			tp0 = false;
			y=[];
		});
		$("#btn9").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = true;
			tp0 = false;
			y=[];
		});
		$("#btn0").click(function(){
			tp1 = false;
			tp2 = false;
			tp3 = false;
			tp4 = false;
			tp5 = false;
			tp6 = false;
			tp7 = false;
			tp8 = false;
			tp9 = false;
			tp0 = true;
			y=[];
		});
		(function() {
			var lastTime = 0;
			var vendors = ['webkit', 'moz'];
			for(var xx = 0; xx < vendors.length && !window.requestAnimationFrame; ++xx) {
				window.requestAnimationFrame = window[vendors[xx] + 'RequestAnimationFrame'];
				window.cancelAnimationFrame = window[vendors[xx] + 'CancelAnimationFrame'] ||
											  window[vendors[xx] + 'CancelRequestAnimationFrame'];
			}
		
			if (!window.requestAnimationFrame) {
				window.requestAnimationFrame = function(callback, element) {
					var currTime = new Date().getTime();
					var timeToCall = Math.max(0, 16.7 - (currTime - lastTime));
					var id = window.setTimeout(function() {
						callback(currTime + timeToCall);
					}, timeToCall);
					lastTime = currTime + timeToCall;
					return id;
				};
			}
			if (!window.cancelAnimationFrame) {
				window.cancelAnimationFrame = function(id) {
					clearTimeout(id);
				};
			}
		}());
		begin();
	});console.log("\u002f\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u000d\u000a\u0020\u002a\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u002a\u0009\u0009\u000d\u000a\u0020\u002a\u0020\u0009\u0009\u0009\u0009\u0009\u0009\u0020\u0020\u0020\u0020\u0020\u0020\u4ee3\u7801\u5e93\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u002a\u000d\u000a\u0020\u002a\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0077\u0077\u0077\u002e\u0064\u006d\u0061\u006b\u0075\u002e\u0063\u006f\u006d\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u002a\u000d\u000a\u0020\u002a\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0009\u0009\u0020\u0020\u52aa\u529b\u521b\u5efa\u5b8c\u5584\u3001\u6301\u7eed\u66f4\u65b0\u63d2\u4ef6\u4ee5\u53ca\u6a21\u677f\u0009\u0009\u0009\u002a\u000d\u000a\u0020\u002a\u0020\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u0009\u002a\u000d\u000a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002a\u002f");