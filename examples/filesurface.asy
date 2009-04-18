import graph3;
import palette;

size3(200,IgnoreAspect);

file in=line(input("filesurface.dat"));
real[] x=in;
real[] y=in;

real[][] f=dimension(in,0,0);

triple f(pair t) {
  int i=round(t.x);
  int j=round(t.y);
  return (x[i],y[j],f[i][j]);
}

surface s=surface(f,(0,0),(x.length-1,y.length-1),x.length-1,y.length-1);
real[] level=uniform(min(f)*(1-sqrtEpsilon),max(f)*(1+sqrtEpsilon),4);

s.colors(palette(s.map(new real(triple v) {return find(level >= v.z);}),
                 Rainbow())); 

draw(s,meshpen=thick());

triple m=currentpicture.userMin;
triple M=currentpicture.userMax;
triple target=0.5*(m+M);
currentprojection=perspective(camera=target+realmult(dir(68,225),M-m),
                              target=target);

xaxis3("$x$",Bounds(),InTicks);
yaxis3("$y$",Bounds(),InTicks(Step=1,step=0.1));
zaxis3("$z$",Bounds(),InTicks);