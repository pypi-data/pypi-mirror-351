# Ghost Your BE 🚀

A powerful tool for generating mock data and APIs, designed to streamline frontend development and testing workflows.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

- **Schema-based Data Generation**: Generate realistic mock data from YAML schema definitions
- **Database Integration**: Direct data insertion into MySQL, MongoDB, and other databases
- **API Mocking**: Create mock APIs for frontend development
- **API Comparison**: Compare mock APIs with real endpoints
- **Smart Data Generation**: Support for Vietnamese data types (names, addresses, phone numbers)
- **Flexible Output**: Export data to JSON, CSV, or directly to databases

## 🚀 Quick Start

### Installation

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install ghost-your-be
```

### Basic Usage (if you not development, just remove "poetry run" before run command)

1. **Generate Data from Schema**:
```bash
poetry run ghost-your-be generate \
  --schema schema.yml \
  --count 10 \
  --db-url mysql+pymysql://user:pass@localhost:3306/db \
  --table users \
  --drop-table
```

2. **Create Mock API**:
```bash
poetry run ghost-your-be mock-api \
  --schema schema.yml \
  --port 8000
```

3. **Compare APIs**:
```bash
poetry run ghost-your-be compare \
  --mock http://localhost:8000/mock/users \
  --real http://api.example.com/users
```

## 📝 Schema Definition

Create a `schema.yml` file to define your data structure:

```yaml
tables:
  users:
    fields:
      id: { type: integer, primary_key: true }
      name: { type: string, faker: vietnam_name }
      phone: { type: string, faker: vietnam_phone }
      address: { type: string, faker: vietnam_address }
```

In addition, there are providers such as(add "vietnam" before "_".Example: vietmam_email - for email): _email, _motocycle, _car, _year, _month, _day, _date, _time, _password, _username, _age, _gender, _job, _salary, _comapny, _school

## 🔧 Configuration

### Database URLs

- **MySQL**:
```
mysql+pymysql://user:password@host:port/database
```

- **MongoDB**:
```
mongodb://user:password@host:port/database
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--schema` | Path to schema YAML file | Required |
| `--count` | Number of rows to generate | 5 |
| `--db-url` | Database connection URL | None |
| `--table` | Table/collection name | None |
| `--output` | Output file (JSON/CSV) | None |
| `--drop-table` | Drop table before insert | False |

## 🛠️ Development

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)
- MySQL/MongoDB (for database features)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/ghost-your-be.git
cd ghost-your-be

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running Tests

```bash
poetry run pytest
```

## 📚 API Reference

### Mock API Endpoints

- `GET /mock/{endpoint}`: Generate mock data for specified endpoint
  - Query Parameters:
    - `count`: Number of records to generate (default: 5)

### Data Generation

The tool supports various data types and faker providers:

- `vietnam_name`: Vietnamese names
- `vietnam_phone`: Vietnamese phone numbers
- `vietnam_address`: Vietnamese addresses
- Custom faker providers can be added

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Faker](https://github.com/joke2k/faker) for data generation
- [FastAPI](https://fastapi.tiangolo.com/) for the mock API server
- [SQLAlchemy](https://www.sqlalchemy.org/) for database operations

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ by [Doi Tuyen]
