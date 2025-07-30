# mkcrack

`mkcrack` is a simple educational Python library designed to demonstrate password cracking using **Yescrypt** hashes and custom wordlists. This tool can be helpful for understanding the basics of hashing, password security, and how wordlist-based attacks work.

⚠️ **Disclaimer:**  
This tool is intended for **educational and ethical purposes only**. Do not use `mkcrack` for any illegal or unauthorized activities. The author is not responsible for any misuse of this library. Use responsibly and only in legal contexts (e.g., security research, academic learning, personal testing).

---

## 🔧 Features

- Crack Yescrypt hashes using a custom or common wordlist.
- Supports commonly used wordlists like `rockyou.txt` (available in Kali Linux or for download).
- Easily extendable: add your own passwords to the wordlist for better results.

---

## 🚀 Installation

install via pip:

pip install mkcrack

Install dependencies 

Ensure you have a wordlist file (e.g., rockyou.txt or your own custom list). You can download rockyou.txt from trusted sources or use your own list.

🎓 Usage
Here’s an example usage in Python:

python

from mkcrack import mkcrack

# Example: Start cracking!
mkcrack.mkcrack_hash_yescrypt()
When you run the function, it will ask for:

The path to your wordlist file (e.g., /usr/share/wordlists/rockyou.txt).

The tool will try each word in the list against a predefined Yescrypt hash.

💡 Wordlist Recommendations
For better results:

Use rockyou.txt (commonly found in Kali Linux: /usr/share/wordlists/rockyou.txt).

Add more passwords to the list based on your target scenario.

You can create a custom wordlist by adding words manually:

echo "qwerty" >> mylist.txt
echo "password123" >> mylist.txt

📜 License
MIT License

🌍 Contribution
Feel free to contribute by forking the repo, opening issues, or submitting pull requests! Let’s make learning fun together! 🎓

🔒 Reminder
This tool is strictly for educational use. Do not use it for illegal purposes or without authorization. Ethical hacking only! 🕵️‍♂️

Happy learning! 🎉
