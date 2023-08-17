import subprocess


def patch_boot_with_magiskboot(input_img, output_img, magisk_patched_img):
    magiskboot_path = "./magiskboot.exe"  # Update with the correct path to magiskboot

    command = [magiskboot_path, "repack", input_img, magisk_patched_img, output_img]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Patch successful!")
    else:
        print("Patch failed.")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)


if __name__ == "__main__":
    input_img = "input_boot.img"  # Replace with your input boot image file
    output_img = "patched_output_boot.img"  # Replace with the desired patched output boot image file
    magisk_patched_img = "magisk_patched.img"  # Path to your Magisk patched image

    patch_boot_with_magiskboot(input_img, output_img, magisk_patched_img)
