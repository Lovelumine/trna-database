# ENSURE backend systemd service

This starts the Flask/Gunicorn backend without `screen`.

Install and start the user service:

```bash
./deploy/systemd/install-user-service.sh
```

Check status:

```bash
systemctl --user status ensure-backend.service
```

Follow logs:

```bash
journalctl --user -u ensure-backend.service -f
```

Stop/start/restart:

```bash
systemctl --user stop ensure-backend.service
systemctl --user start ensure-backend.service
systemctl --user restart ensure-backend.service
```

Enable startup before the desktop user logs in:

```bash
sudo loginctl enable-linger "$USER"
```

Disable:

```bash
systemctl --user disable --now ensure-backend.service
```
