Here is the **updated full `README.md`** with all relevant sections, including installation from PyPI and TestPyPI, publishing instructions, developer mode, and licensing.

---

### 📄 Final `README.md` for `appwrite-sync`

````markdown
# appwrite-sync

**`appwrite-sync`** is a CLI tool to automate the creation and synchronization of Appwrite database collections from a JSON schema. It's designed for developers who want to version and manage their Appwrite collections in a clean and repeatable way—ideal for CI/CD, team collaboration, and structured schema design.

---

## 🚀 Features

- 🔁 Sync collections, attributes, relationships, and indexes
- 📁 Reads from a single `schema.json` definition
- ⚙️ Supports all common attribute types including `string`, `enum`, `relationship`
- ✅ Idempotent: avoids duplication and handles existing resources gracefully
- 🛠 CLI-first: easily scriptable and automatable
- 📦 Packaged and installable from PyPI

---

## 📦 Installation

### From PyPI

```bash
pip install appwrite-sync
````

### From TestPyPI (optional testing)

```bash
pip install --index-url https://test.pypi.org/simple/ appwrite-sync
```

---

## 🧰 Usage

### 1. Initialize a Folder

Generate a sample `.env` file and `schema.json` template in your current directory:

```bash
appwrite-sync init
```

### 2. Configure `.env`

```env
ENDPOINT=http://localhost/v1
PROJECT_ID=your-project-id
DB_ID=your-database-id
API_KEY=your-appwrite-api-key
```

### 3. Define Your Schema

Edit `schema.json` to define collections, attributes, and indexes. Example:

```json
{
  "users": {
    "name": "Users",
    "attributes": {
      "email": {
        "type": "email",
        "required": true
      },
      "role": {
        "type": "enum",
        "required": true,
        "elements": ["admin", "user"]
      }
    },
    "indexes": [
      {
        "key": "unique_email",
        "type": "unique",
        "attributes": ["email"]
      }
    ]
  }
}
```

### 4. Sync to Appwrite

Make sure your `.env` is sourced:

```bash
source .env
```

Then run:

```bash
appwrite-sync sync
```

Or pass DB ID directly:

```bash
appwrite-sync sync --db-id your-db-id
```

---

## ✅ Supported Attribute Types

* `string`, `email`, `url`, `integer`, `boolean`, `datetime`
* `enum` with `elements`
* `relationship` with `relatedCollection`, `relationType`, and `twoWay`

---

## 🧪 Development (Editable Install)

```bash
git clone https://github.com/aboidrees/appwrite-sync.git
cd appwrite-sync
pip install -e . --config-settings editable_mode=compat
```

---

## 📤 How to Publish to PyPI

### Step 1: Build the package

```bash
python -m build
```

### Step 2: Upload to PyPI

```bash
twine upload dist/*
```

> **To upload to TestPyPI instead**:
>
> ```bash
> twine upload --repository-url https://test.pypi.org/legacy/ dist/*
> ```

### Step 3: Install from PyPI

```bash
pip install appwrite-sync
```

---

## 🧾 License

This project is licensed under the MIT License.
See the [`LICENSE`](LICENSE) file for full details.

---

## 👨‍💻 Author

Developed by \[Muhammad Yousif]

GitHub: [https://github.com/aboidrees](https://github.com/aboidrees)

```

---

Would you like me to also generate a matching `LICENSE` file now? If so, let me know what name you want to appear in the copyright.
```
