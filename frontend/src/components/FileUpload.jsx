
function FileUpload({ onFileSelect }) {
  return (
    <input
      type="file"
      onChange={(e) => onFileSelect(e.target.files[0])}
      required
    />
  );
}

export default FileUpload;
