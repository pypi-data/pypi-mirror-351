<p align="center">
  <h1 align="center">🦊 ProxyFox</h1>
  <p align="center">A fast and simple proxy fetching library for Python</p>
</p>

<p align="center">
  <a href="https://pypi.org/project/proxyfox/">
    <img src="https://img.shields.io/pypi/v/proxyfox" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/proxyfox/">
    <img src="https://img.shields.io/pypi/pyversions/proxyfox" alt="Python Versions">
  </a>
  <a href="https://github.com/redmoon0x/proxyfox/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/redmoon0x/proxyfox" alt="License">
  </a>
</p>

---

## 🚀 Features

- 🔥 **Simple Interface** - Get proxies in just one line of code
- 🔄 **Auto-updating Pool** - Keep your proxies fresh
- 🌍 **Country Filtering** - Get proxies from specific countries
- ⚡ **Speed Filtering** - Get only fast proxies
- 🔒 **Protocol Support** - HTTP and HTTPS proxies
- 💪 **Flexible API** - Simple for beginners, powerful for experts

## 📦 Installation

```bash
pip install proxyfox
```

## 🎯 Quick Start

### Get a Single Proxy

```python
import proxyfox

# Get any proxy
proxy = proxyfox.get_one()
print(proxy)  # Output: '11.22.33.44:8080'

# Get specific proxy type
proxy = proxyfox.get_one(
    protocol='https',  # 'http' or 'https'
    country='US',     # country code
    max_speed_ms=1000 # speed filter
)
```

### Get Multiple Proxies

```python
# Get 5 proxies
proxies = proxyfox.get(5)

# Get 3 fast proxies from UK
proxies = proxyfox.get(
    3, 
    country='UK',
    max_speed_ms=1000
)
```

### Use Auto-updating Pool

```python
# Create a pool that updates every 5 minutes
pool = proxyfox.create_pool(
    size=10,               # pool size
    refresh_interval=300,  # update interval in seconds
    protocol='https'       # optional filters
)

# Get a fresh proxy
proxy = pool.get()

# Get all current proxies
all_proxies = pool.all()
```

## 🛠️ Advanced Usage

### Using the ProxyFetcher Class

```python
fetcher = proxyfox.ProxyFetcher()

# Get fast proxies
proxies = fetcher.get_fast_proxies(limit=5)

# Get country-specific proxies
us_proxies = fetcher.get_country_proxies('US')

# Get protocol-specific proxies
https_proxies = fetcher.get_https_proxies()
```

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `protocol` | 'http' or 'https' | `protocol='https'` |
| `country` | Two-letter country code | `country='US'` |
| `max_speed_ms` | Maximum response time | `max_speed_ms=1000` |

## 📝 Example

```python
import proxyfox

# Create an auto-updating pool of fast HTTPS proxies
pool = proxyfox.create_pool(
    size=10,
    refresh_interval=300,
    protocol='https',
    max_speed_ms=1000
)

# Get a proxy whenever needed
proxy = pool.get()
print(f"Using proxy: {proxy}")

# Get all current proxies
all_proxies = pool.all()
for proxy in all_proxies:
    print(f"Available: {proxy}")
```

## 📚 Documentation

For more examples and detailed documentation, visit our [GitHub repository](https://github.com/redmoon0x/proxyfox).

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Dev shetty (deviprasadshetty400@gmail.com)
