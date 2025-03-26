# Total Atacado T1

A desktop application built with PySide6 for ticket code validation.

## Features

- Modern and responsive user interface
- Real-time input validation
- Smooth animations and visual feedback
- Custom styled components
- Error handling with visual indicators

## Requirements

- Python 3.x
- PySide6
- qt-material (optional for theming)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/totalatacadot1.git
```

```bash
cd totalatacadot1
```

```bash
pip install -r requirements.txt
```

## Usage

Run the application using:

```bash
python src/totalatacadot1/app.py
```

## 2. Database

docker volume create oracle_db_data

docker run -d --name oracle_db \
-p 1521:1521 -p 5500:5500 \
-e ORACLE_PWD=CAIXA \
-v oracle_db_data:/opt/oracle/oradata \
container-registry.oracle.com/database/express:21.3.0-xe

docker exec -i oracle_db sqlplus sys/CAIXA@//localhost:1521/XEPDB1 as sysdba <<EOF
CREATE USER CAIXA IDENTIFIED BY CAIXA;
GRANT CREATE SESSION TO CAIXA;
GRANT CREATE TABLE TO CAIXA;
GRANT UNLIMITED TABLESPACE TO CAIXA;
GRANT CREATE SEQUENCE TO CAIXA;
GRANT CREATE PROCEDURE TO CAIXA;
EOF

docker exec -i oracle_db sqlplus CAIXA/CAIXA@localhost:1521/XEPDB1 as sysdba <<EOF
SELECT username FROM dba_users WHERE username = 'CAIXA';
EOF

ACCESS:
docker exec -i oracle_db sqlplus CAIXA/CAIXA@localhost:1521/XEPDB1

## Application Structure

- `MainWindow`: Main application window with icon and geometry settings
- `MainWidget`: Core widget containing the application's interface
  - Input field for ticket code
  - Save button with visual feedback
  - Animated error handling
  - Success/Error message dialogs

## UI Features

- Responsive input field with hover and focus states
- Animated error feedback
- Modern button design with hover effects
- Clean and intuitive layout
- Message dialogs for operation feedback

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[MIT License](LICENSE)
