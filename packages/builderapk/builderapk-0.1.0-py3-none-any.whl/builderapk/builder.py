# builderapk/builder.py
import subprocess
import os

def build_apk(project_path, build_type='debug', sdk_path=None):
    """
    Membangun proyek Android menjadi APK menggunakan Gradle.

    Args:
        project_path (str): Jalur ke direktori proyek Android.
        build_type (str): Jenis build, 'debug' atau 'release'. Default: 'debug'.
        sdk_path (str, optional): Jalur ke Android SDK, jika diperlukan.

    Returns:
        str: Jalur ke file APK yang dihasilkan.

    Raises:
        ValueError: Jika build_type bukan 'debug' atau 'release'.
        Exception: Jika proses build gagal.
        FileNotFoundError: Jika APK tidak ditemukan setelah build.
    """
    # Validasi build_type
    if build_type not in ['debug', 'release']:
        raise ValueError("build_type harus 'debug' atau 'release'")

    # Set jalur ke Android SDK jika disediakan
    if sdk_path:
        os.environ['ANDROID_HOME'] = sdk_path

    # Tentukan perintah Gradle berdasarkan build_type
    gradle_task = 'assembleDebug' if build_type == 'debug' else 'assembleRelease'

    # Jalankan perintah Gradle di direktori proyek
    try:
        result = subprocess.run(
            ['./gradlew', gradle_task],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True
        )
        print("Output build:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Kesalahan build:\n", e.stderr)
        raise Exception(f"Build gagal: {e.stderr}")

    # Tentukan jalur ke APK yang dihasilkan
    apk_path = os.path.join(
        project_path,
        'app',
        'build',
        'outputs',
        'apk',
        build_type,
        f'app-{build_type}.apk'
    )

    # Periksa apakah APK berhasil dibuat
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK tidak ditemukan di {apk_path}")

    return apk_path
