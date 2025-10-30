## Muti-Tenant SAS

# install uv (Windows)

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

```


# install uv (Linux/MacOS)

```
curl -LsSf https://astral.sh/uv/install.sh | sh

```


# Clone the repo

```
git clone https://github.com/emekadefirst/NoteApp-Saas.git SAASTEST

```

# Change Directory into SAASTEST

```
uv sync --frozen

```

# Activate the env


 .venv\Scripts\activate (windows CMD)

source .venv\Scripts\activate (windows GitBash)

source .venv\bin\activate  (Linux/MacOS terminal)


# Run Seed Data for Admin, Permission and Permission Groups

```
uv run seed

```


# run server

```
uv run dev

```


# You should have this in your envfile


DB_URI=mongodb://localhost:27017/sas

SECRET_KEY=69ba0cd800df61f72935fbc3bb86680296b83796f5e3034c36558a55d432140d
DEBUG=True
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRY=15
JWT_ACCESS_SECRET=e1d26c4cadf973441fd06947157f116dee9fdec5299dcee438a4f280706253b6
JWT_REFRESH_EXPIRY=7
Here’s a clean, professional, and well-structured rewrite of your **README.md** file — properly formatted for GitHub or any project documentation platform:

---

# 🏢 Multi-Tenant SaaS Backend

A modular and scalable **multi-tenant SaaS backend** built with **FastAPI** and **MongoDB**, supporting user authentication, role-based permissions, and organization management.

---

## 🚀 Setup Guide

### 1️⃣ Install **uv** (Package & Environment Manager)

#### 🪟 Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 🐧 Linux / 🍎 macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/emekadefirst/NoteApp-Saas.git SAASTEST
cd SAASTEST
```

---

### 3️⃣ Install Dependencies

```bash
uv sync --frozen
```

---

### 4️⃣ Activate the Virtual Environment

#### Windows (CMD)

```bash
.venv\Scripts\activate
```

#### Windows (Git Bash)

```bash
source .venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

---

### 5️⃣ Seed Initial Data

Run this command to create:

* Default **Admin user**
* **Permissions**
* **Permission Groups**

```bash
uv run seed
```

---

### 6️⃣ Start the Development Server

```bash
uv run dev
```

Your server should now be running on [http://localhost:8080](http://localhost:8080) 🎉

---

## ⚙️ Environment Configuration

Make sure your `.env` file includes the following variables:

```env
DB_URI=mongodb://localhost:27017/sas

SECRET_KEY=69ba0cd800df61f72935fbc3bb86680296b83796f5e3034c36558a55d432140d
DEBUG=True

JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRY=15
JWT_ACCESS_SECRET=e1d26c4cadf973441fd06947157f116dee9fdec5299dcee438a4f280706253b6
JWT_REFRESH_EXPIRY=7

ADMIN_EMAIL=demo@admin.com
ADMIN_FIRSTNAME=John
ADMIN_LASTNAME=Doe
ADMIN_PASSWORD=Password230$
ADMIN_PHONENUMBER=09123086107
```

---

## 🧩 Features

* Multi-Tenant Architecture
* Role-Based Access Control (RBAC)
* Admin & Organization Management
* Modular Design for Easy Expansion
* FastAPI-Powered Performance
* MongoDB Persistence

---

## 🧑‍💻 Development

Run the app locally, edit source files, and changes will automatically reload.

---

## 🛠 Tech Stack

| Component       | Technology   |
| --------------- | ------------ |
| Backend         | FastAPI      |
| Database        | MongoDB      |
| Package Manager | uv           |
| ORM / ODM       | Motor        |
| Auth            | JWT-based    |
| Language        | Python 3.11+ |

---

ADMIN_EMAIL=demo@admin.com
ADMIN_LASTNAME=John
ADMIN_PASSWORD=Password230$
ADMIN_FIRSTNAME=Doe
ADMIN_PHONENUMBER=09123086107