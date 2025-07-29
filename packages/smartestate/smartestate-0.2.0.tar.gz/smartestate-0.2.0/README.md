## SmartEstate

### About

Django app for real estate brokers. If you are a real estate broker, you can use this
to power your website, and the backend will allow you to manage your listings, apartments,
offers for sale, as well as potentials - renters, buyers, etc.

### Roadmap

This is a legacy project from ca. 3 years ago, which I am recently revisiting. It is not stable,
and not ready for production use, but I am working to release a stable version soon.
Until the stable version 1.0 appears, things can and will break between releases without notice.

### Installing

#### Install platform requirements

These are required for the MySQL driver, see https://github.com/PyMySQL/mysqlclient

##### Debian/Ubuntu

```
apt install  python3-dev default-libmysqlclient-dev  build-essential  pkg-config
```

##### Red Hat / CentOS

```
yum install python3-devel mysql-devel pkgconfig
```

##### Other distros / macOS / Windows

See the [docs for mysqlclient](https://github.com/PyMySQL/mysqlclient), you probably have to
install similar libraries. Otherwise, if you don't need MySQL (ie. using SQLite locally),
you can comment out `mysqlclient` from _requirements.txt_ and it should work.

#### Install Python app dependencies

```python
pip install -r requirements.txt
```

### Usage

#### Local

`cp .env.example .env` and configure with appropriate values.

Then, usual Django setup:

* `python manage.py migrate`
* `python manage.py createsuperuser`
* `python manage.py runserver`
* Unit tests: `python manage.py test`


Set up the cookie group in the Django admin, and make it optional for the cookie banner to appear.

#### Production

Good luck ;-)
