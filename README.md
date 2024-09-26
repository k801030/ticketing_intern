# 票務工讀生

## For Users

### Prerequisites

pip & python

### Installation

```
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Execution

```
python intern.py -h
```

### Sample Command

```
python intern.py \
    --facebook_account abc@gmail.com \
    --facebook_password my_password_123 \
    --page https://tixcraft.com/activity/detail/24_asmrmaxxx
```

## FAQ

### Could I select the dates, seats?

Currently, the intern will select date and seat randomly

### How to run multiple windows?

> The feature is currently disabled

You can achieve it by specifying the number of interns

```
python intern.py --num_of_interns N
```

## Troubleshooting

### Sorry! Something went wrong :(

Please go back to the previous page, and the web app will continue

If that cannot be resolved, then layoff and hire another intern

### 504 Gateway Time-out

Please close the window, and re-hire the intern