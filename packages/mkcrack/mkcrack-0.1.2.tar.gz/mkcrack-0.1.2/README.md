# mkcrack 🔐

A Python tool for **educational password cracking** using Yescrypt hashes.  
Learn how password hashing works, test password strength, and understand the importance of strong password choices.

> ⚠️ **Disclaimer:**
This tool is for **educational purposes only**. Do not use it for unauthorized access, hacking, or illegal activities. Always test on your own systems and stay ethical.

---

## 🧊 What is Yescrypt?

✅ Yescrypt is an advanced password hashing algorithm used in modern Linux systems.  
✅ It slows down brute-force attacks using CPU and memory-intensive operations.  
✅ It incorporates **salts** and is resistant to side-channel and timing attacks.

In short:  
🛡️ Yescrypt protects your passwords, but **strong passwords** are still essential.

---

## 🚀 Installation

Install the library via pip:

```bash
pip install mkcrack

```


**📖 Usage Steps**

Follow these steps to test cracking a Yescrypt hash:

1️⃣ Find Your Yescrypt Hash

Open a terminal in your Linux system.

Use the following command to safely view your hash (replace yourusername with your actual username):

```bash

sudo grep '^yourusername:' /etc/shadow

```


The output will look like this:


```bash
yourusername:$y$j9T$jtPDS9VZ13n3wXmFOvYIG1$HCmUaqmBK.3U2H2MtN9audXFbBUwvunR01ghnKoGF/9:...
```

>🔒 In Linux systems, user login passwords are not stored in plaintext (for security reasons). Instead, they are stored in hashed form (scrambled using algorithms like Yescrypt, SHA-512, etc.).
---

Copy the part starting with $y$ — this is your Yescrypt hash.

2️⃣ Create a Wordlist
Create a file named mywords.txt in your project directory.

Add possible password guesses (one per line):
```bash
nginx
Copy
Edit
nginx
password123
letmein
supersecure
mypassword
```
This is your dictionary for guessing.

3️⃣ Create the Python Script
Create a new Python file named myfunc.py.

Add the following code:

```python
from mkcrack import cracker 

# Replace this with your actual Yescrypt hash
stored_hash = '$y$j9T$jtPDS9VZ13n3wXmFOvYIG1$HCmUaqmBK.3U2H2MtN9audXFbBUwvunR01ghnKoGF/9'

# Path to your wordlist file
wordlist_path = 'mywords.txt'

# Attempt to crack the hash
password = cracker.crack_yescrypt(stored_hash, wordlist_path)

if password:
    print(f"Cracked password: {password}")
else:
    print("Password not found in the wordlist.")
```
4️⃣ Run the Script
In your terminal, execute the script:

```bash

python3 myfunc.py
```
If the password is in your wordlist, you’ll see:

```bash
Cracked password: letmein

Otherwise:

Password not found in the wordlist.
```
**⚠️ Why You Should NEVER Share Your Password Hash
Even though a hash looks scrambled, sharing it can be risky:**

Attackers can attempt offline brute-force attacks.

Weak passwords can be cracked quickly.

**Hash reuse risk:**

Cracking one hash can compromise multiple accounts.

Targeted attacks become easier with your hash in hand.

👉 Treat your password hash like a secret key—never share it publicly.

**📚 Final Thoughts**

✅ Yescrypt is strong, but password security is a team effort:

Use strong, unique passwords.

Configure your system properly.

Understand how hashes work.

Stay safe, stay ethical, and use this knowledge for good! ✨


**🌟 Want to contribute?**

Feel free to open issues, suggest features, or submit pull requests. 

Let’s learn and grow together!

---








