# Pustaka Python untuk membangun proyek Android menjadi APK.

## Instalasi

```
pip install builderapk
```

## Penggunaan

```
from builderapk import build_apk

project_path = '/path/to/android/project'
apk = build_apk(project_path, build_type='debug')
print(f"APK berhasil dibangun di: {apk}")LisensiMIT License### 6. `pyproject.toml`
File ini mendefinisikan sistem build.

```
