from django.shortcuts import render
import requests
import hashlib
import random

# Function to generate a random password
def generate_sentence():
    adj = ("Cute", "Lazy", "Dirty", "Weird", "Spicy", "Lovely", "Sussy")
    nouns = ("Eagle", "Dog", "Car", "Aggie", "Girl", "Monkey", "Troll", "Baka", "Nugget")
    verbs = ("Runs", "Hits", "Jumps", "Drinks", "Eats", "Skips")
    adv = ("Crazily", "Easily", "Foolishly", "Merrily", "Frantically", "Awkwardly")
    dig = ("1", "2", "3", "4", "5", "6", "7", "8", "9")
    spec = ("!", "?", ":", "^", "#", "@")

    noun = random.choice(nouns)
    verb = random.choice(verbs)
    adverb = random.choice(adv)
    adjective = random.choice(adj)
    digit = random.choice(dig)
    special = random.choice(spec)
    sentence = f"{adjective}{noun}{verb}{adverb}{digit}{special}"
    return sentence

def index(request):
    context = {
        "title": "Password Strength Analyzer",
        "generated_password": None,
    }
    
    if request.method == 'POST':
        if 'generate-password' in request.POST:
            # Generate a new password if the 'Generate Password' button is clicked
            context["generated_password"] = generate_sentence()
        else:
            # Handle password strength checking logic as before
            password = request.POST.get('password-field', '')
            l, u, p, d = 0, 0, 0, 0
            capitalalphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            smallalphabets = "abcdefghijklmnopqrstuvwxyz"
            specialchar = "!@#$%^&*()_+-=,./<>?:;"
            digits = "0123456789"
            
            if len(password) >= 0:
                for char in password:
                    if char in smallalphabets:
                        l += 1
                    if char in capitalalphabets:
                        u += 1
                    if char in digits:
                        d += 1
                    if char in specialchar:
                        p += 1

            messages = []
            if l >= 1 and u >= 1 and p >= 1 and d >= 1 and l + p + u + d == len(password):
                messages.append("Valid Password")
            else:
                messages.append("Invalid Password")
                if l < 1: 
                    messages.append("Lowercase characters needed")
                if u < 1: 
                    messages.append("Uppercase characters needed")
                if p < 1: 
                    messages.append("Special characters needed")
                if d < 1: 
                    messages.append("Digits needed")
                if l + p + u + d < 16: 
                    messages.append(f"Your password should be at least 16 characters. This one is only {len(password)} characters")

            if len(password) > 0:
                check_password(password, messages)

            context['messages'] = messages

    return render(request, "index.html", context)

def check_password(password, messages):
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)
    
    if response.status_code == 200:
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                messages.append(f"The password '{password}' has been compromised {count} times. It is not advised to use this password.")
                return 0
        messages.append(f"The password '{password}' has not been compromised.")
        return 1
    else:
        messages.append(f"Error checking password: {response.status_code}")
