# Django Rest Framework and Celery using Docker
Django Rest Framework, Celery, Redis and PostgreSQL, with sensible defaults, running in Docker containers, with AWS config and helpers.


## Dev
We use [Docker](https://docs.docker.com/docker-for-mac/) and `docker-compose` in development to package and deploy our application.

To decrypt env vars in `env.dev` and run dev, execute `./dev.sh`. To see which containers are running, run `docker-compose ps`. To stop all containers, run `docker-compose stop`.

To blow containers away and build them from scratch, use `docker-compose rm` then `./dev.sh`.


### Prerequisites
Run commands in `citext.sql` in database.

~~~sh
python manage.py makemigrations users main
python manage.py migrate users
python manage.py migrate main
python manage.py migrate
~~~


### Logs
__PostgreSQL__: open `/var/lib/postgresql/data/postgresql.conf` in the __db__ container, also at `dbdata/postgresql.conf`, and add the following:

~~~sh
logging_collector = 'on'
log_statement = 'all'
log_line_prefix = '%t'
~~~

Then restart the db container, `docker-compose restart db`. Tail logs like this:

~~~sh
less +F dbdata/pg_log/`ls -1 dbdata/pg_log/ | tail -1`
~~~


## Deploy
For devs only. Run `./build.sh`. This will decrypt production env vars and build the `backend_base` and `nginx` images.

Then run `./deploy.sh <image_name>`, and finish from the AWS Elastic Beanstalk console.


### Rollback
Run `./retag_latest.sh <image_name> <tag>` to tag an (old) image with the __latest__ tag, then deploy from the AWS Elastic Beanstalk console. All images are tagged with git hash of source repo used to build image. These git hashes also live in the `appversion` table.


### Manual deploy
Tag and push these images to [ECR](https://us-west-2.console.aws.amazon.com/ecs/home?region=us-west-2#/repositories/), then deploy from the AWS Elastic Beanstalk console.

~~~sh
# log in
aws ecr get-login --no-include-email --region us-west-2

# example: push the latest nginx image to ECR
docker tag nginx:latest 306439459454.dkr.ecr.us-west-2.amazonaws.com/nginx:latest
docker push 306439459454.dkr.ecr.us-west-2.amazonaws.com/nginx:latest
~~~

__Make sure Elastic Beanstalk IAM user has permissions to read from ECR__. If not deploy will fail.


## Documentation
Additional documentation is generated programmatically.


### Database schema UML
Using the [graph_models](https://django-extensions.readthedocs.io/en/latest/graph_models.html) extension.

- on your local machine, run `brew install graphviz`
- in Docker container, run `python manage.py graph_models -a -X BaseModel > /tmp/uml.dot`
- copy dot file to your machine
- run `dot uml.dot -Tpng -o uml.png` to generate image


### Browsable API docs
Using this [DRF -> OpenAPI](https://github.com/axnsan12/drf-yasg/) tool. See <https://SITE_URL/api/swagger/> or <https://SITE_URL/api/redoc/>.


## Endpoints
NGINX forces HTTPS for requests to these endpoints. It also compresses responses.

- API: <https://api.SITE_URL/api/>
- Celery flower: <https://api.SITE_URL/flower/>
- Django admin: <https://api.SITE_URL/admin/>


## AWS
We manage our infrastructure with AWS. We deploy to Elastic Beanstalk multi container Docker environments. This means the same `Dockerfile`s that build our images in dev build them in production.


### SSL
We use ACM to generate certificates. __ACM certificates can only be used with AWS load balancers and CloudFront distributions,__ but this is what we use to serve both our web app and our API. Here's an [excellent tutorial](https://gist.github.com/bradwestfall/b5b0e450015dbc9b4e56e5f398df48ff) on how to set up CloudFront for sites served by S3. 

__The certificate must be created in `us-east-1` region to be used with CloudFront__. This isn't well-documented. See certificate [here](https://console.aws.amazon.com/acm/home?region=us-east-1).

Traffic between our backend AWS instances is not encrypted, because [it's not necessary](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-endtoend.html).

>Terminating secure connections at the load balancer and using HTTP on the backend may be sufficient for your application. __Network traffic between AWS resources cannot be listened to by instances that are not part of the connection__, even if they are running under the same account.


### RDS and ElastiCache
Our PostgreSQL and Redis instances are managed by [RDS](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.RDS.html) and [ElastiCache](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.ElastiCache.html).

There are many ways to grant RDS/ElastiCache ingress access to EC2 instances, for example:

- find the __default VPC security group__ that is assigned to both ElastiCache and RDS instances
- add ingress rules to this group on ports 5432 and 6379 for `api` and `celery-beat` environment security groups

However, this creates an explicit dependency between the EC2 instance and our data stores. This means __we won't be able rebuild or terminate our environment__.

If you try to do so, __you're entering a world of pain__. Instead of failing fast, AWS kill your EC2 instances, then hang for an hour or more while it periodically informs you that your security groups can't be deleted.

Here's how to do it right: [Grant Elastic Beanstalk environment access to RDS and ElastiCache automatically](https://notebookheavy.com/2017/06/22/elastic-beanstalk-rds-automatic-access/).

Basically, create a security group called `redis-postgres-read`. Then find the __default VPC security group__ for RDS/ElastiCache and add ingress rules on ports 5432 and 6379 for the `redis-postgres-read` security group. Finally, add this group to __EC2 security groups__ in __Configuration > Instances__ in the Elastic Beanstalk environment console.


#### Testing connections
To test connectivity between EC2 instances and data stores:

~~~sh
# ssh into ec2 box and test connectivity
nc -v <pg_url> 5432
nc -v <redis_url> 6379

# to test credentials for conencting to postgres
sudo yum install postgresql-devel
PGPASSWORD=password psql -h <pg_url> -U postgres -d postgres
~~~


## Env vars
Application configuration is stored in environment variables. These are stored in the `env.dev` and `env.prod` files.

`dev.sh` decrypts env vars in `env.dev` then runs our containers. These env vars are sourced by `docker-compose.yml` and our containers.


### Editing env vars
Make sure you have the `.vault-password` file, with the correct password, in the root of the repo. To decrypt env vars, run `python3 tools/vault.py --infile=env.<dev|prod>`. To encrypt them again run `python3 tools/vault.py --infile=env.<dev|prod> --encrypt`.


### Committing
To make sure unencrypted env vars don't get committed, run `cd .git/hooks && ln -s ../../pre-commit && cd -` from the root of this repo. The `pre-commit` hook fails if env files are not encrypted, or if code doesn't pass `mypy` checks.


## Create StaffUser
~~~sh
# ssh into ec2 instance

# ssh into docker container
sudo docker exec -it <container_id> /bin/ash

source .env
python manage.py staffuser --email <email> --password <password> --full_name <full_name>
# create superuser, or change superuser password
python manage.py staffuser --superuser --email <email> --password <password>
~~~


## Linting and Code Style
Enforced by `flake8` linter.

~~~sh
pip install flake8
pip install flake8-commas
~~~

Check `.flake8` for rules. Run linter on all files, ignoring line length warnings: `flake8 . | grep -v E501`.


### Type Checking with Mypy
~~~sh
pip install mypy
~~~

Check `mypy.ini` for [config options](http://mypy.readthedocs.io/en/latest/config_file.html).

Mypy cheat sheet: <http://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html>.

- `mypy src`
- `mypy src --check-untyped-defs`
