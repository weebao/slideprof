export const upload = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  if (res.ok) {
    return res.json();
  } else {
    throw new Error("Failed to upload file");
  }
}