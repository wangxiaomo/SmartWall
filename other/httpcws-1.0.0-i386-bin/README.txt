HTTPCWS 是一款基于HTTP协议的中文分词系统。

HTTPCWS编译过程：
注：httpcws为静态编译的二进制版本，无需编译，可以直接通过./httpcws执行。如果你需要手工编译，请按照以下方法进行（不建议）：

1、先下载安装libevent：
wget http://www.monkey.org/~provos/libevent-1.4.11-stable.tar.gz
tar zxvf libevent-1.4.11-stable.tar.gz
cd libevent-1.4.11-stable/
./configure --prefix=/usr
make && make install
cd ../
echo "/usr/lib" > /etc/ld.so.conf.d/libevent.conf
/sbin/ldconfig

2、再到http://ictclas.org/Down_share.html下载“ICTCLAS2009简体中文版”-“Linux_C_32”，将解压后的ICTCLAS30.h和libICTCLAS30.a文件放到httpcws的ICTCLAS目录中。

3、编译HTTOCWS：
动态编译：
g++ -o httpcws httpcws.cpp -levent -L./ICTCLAS -lICTCLAS30 -Wall -Wunused -O3 -DOS_LINUX

静态编译：
g++ -o httpcws httpcws.cpp -levent -L./ICTCLAS -lICTCLAS30 -Wall -Wunused -O3 -DOS_LINUX -static-libgcc -pthread -lrt -static


更多内容请访问：
http://code.google.com/p/httpcws
http://blog.s135.com