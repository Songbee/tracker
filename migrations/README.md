We're using Flask-Migrate (which is basically an Alembic wrapper) for migrations.

    docker-compose run web flask db migrate -m 'migration message'
    sudo chown -R username:username migrations/
    # Manually adjust the created migration!
    # Alembic tends to make errors.
    git add migrations/
