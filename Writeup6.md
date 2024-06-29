# Writeup 6 - Fakeroot

## Writeups Map

![Imgur](https://i.imgur.com/gb4HAhr.png)

## Summary

- [14.1 Using fakeroot](#141-using-fakeroot)

## Exploitation

### 14.1 Using fakeroot

> All the following steps can lead here:
>
> - [6.1 Getting SSH access as laurie@borntosec](./Writeup1.md#61-getting-ssh-access-as-laurieborntosec)
> - [9.1 Getting a Terminal access as www-data](./Writeup1.md#91-getting-a-terminal-access-as-www-data)
> - [10.2 Getting SSH access as laurie](./Writeup1.md#102-getting-ssh-access-as-laurie)
> - [11.2 Getting SSH access as thor](./Writeup1.md#112-getting-ssh-access-as-thor)
> - [12. Getting SSH access as zaz](./Writeup1.md#12-getting-ssh-access-as-zaz)

We execute the `fakeroot` command

```text
laurie@BornToSecHackMe:~$ fakeroot
root@BornToSecHackMe:~# id
uid=0(root) gid=0(root) groups=0(root),1003(laurie)
root@BornToSecHackMe:~# whoami
root
```

Even if you don't get proper `root` rights by using this trick, this solution technically follows all the subject's rules about what is `root`

- The user id is 0
- We have a real terminal and we can execute 'whoami' which shows 'root'

![Imgur](https://i.imgur.com/8GM5rZi.png)
