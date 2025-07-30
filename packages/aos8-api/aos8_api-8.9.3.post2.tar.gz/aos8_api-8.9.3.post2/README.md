
# OmniSwitch AOS 8.x RestFul API Builder for Python - **Aos8ApiBuilder**

**Aos8ApiBuilder** is a lightweight python library that enables developers to interact seamlessly with the OmniSwitch RESTful API running version 8.x releases.

---

## ✨ Supported APIs

- System
- Interface
- VLAN 
- VPA
- IP

---

## 🛠️ Built With

- **python 3.8**

```python
    dependencies = [
        "httpx>=0.24.1",
        "requests>=2.31.0",
        "pydantic>=2.0",
        "pybreaker>=0.7.0",
        "backoff>=2.2.1"
    ]
```

## 🚀 Installation


1. pip install aos8x-api

---

## 📦 Usage Guide

### Step 1: Create an object of AosApiClient


```python

    from ApiBuilder import AosApiClientBuilder

    client = (
        AosApiClientBuilder()
        .setBaseUrl("https://<switch-ip-address>")
        .setUsername("<username>")
        .setPassword("<password>")
        .build()
    )

```

### Step 2: Start calling the respective API in your application

```python

    result = client.vlan.create_vlan(vlan_id=999)
    if result.success:
        print("✅ Vlan operation successfully")
    else:
        print(f"❌ VLAN creation failed (diag={result.diag}): {result.error}")
```

## 📚 Documentation

Please check out the details documentation at https://samuelyip74.github.io/Aos8ApiBuilder/intro/#

---

## 📦 Releases

| Version          | Date       | Notes                       |
|------------------|------------|-----------------------------|
| v8.9.03          | 2025-05-28 | Initial release             |
| v8.9.03post1     | 2025-05-28 | Interface, IP API added     |


---

## 📄 License

```
Copyright (c) Samuel Yip Kah Yean <2025>

This software is licensed for personal, non-commercial use only.

You are NOT permitted to:
- Use this software for any commercial purposes.
- Modify, adapt, reverse-engineer, or create derivative works.
- Distribute, sublicense, or share this software.

All rights are reserved by the author.

For commercial licensing or permission inquiries, please contact:
kahyean.yip@gmail.com
```


