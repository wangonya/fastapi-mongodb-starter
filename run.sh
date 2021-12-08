if [ "$1" == dev ]; then
    echo "running dev environment"
    uvicorn app.main:app --reload --port=5000
else
    gunicorn --bind 0.0.0.0:5000 -w 4 -k uvicorn.workers.UvicornWorker app.main:app
fi
