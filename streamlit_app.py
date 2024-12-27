import streamlit as st
import os.path
from io import BytesIO
from PIL import Image, ImagePalette, ImageOps
from pi_heif import register_heif_opener
import tempfile
import pathlib
import shutil

register_heif_opener()

THUMBNAIL_SIZE = (400, 400) 

# Create a palette object
PAL_IMAGE = Image.new("P", (1,1))
PAL_IMAGE.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)

DISPLAY_DITHER = Image.Dither(Image.FLOYDSTEINBERG)

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

temp_dir = tempfile.TemporaryDirectory()
temp_pic_dir = temp_dir.name + "/pic"
os.mkdir(temp_pic_dir)

st.write(temp_dir.name)

uploaded_files = st.file_uploader("Upload your photos", type=['png', 'jpg', 'gif', 'bmp', 'tiff', 'heic'], accept_multiple_files=True)
for uploaded_file in uploaded_files:
    input_image = Image.open(BytesIO(uploaded_file.getbuffer()))
    
    transposed_image = ImageOps.exif_transpose(input_image)
        
    # Get the original image size
    width, height = transposed_image.size
    
    if  width > height:
        target_width, target_height = 800, 480
    else:
        target_width, target_height = 480, 800
    
    # Computed scaling
    scale_ratio = max(target_width / width, target_height / height)
    # Calculate the size after scaling
    resized_width = int(width * scale_ratio)
    resized_height = int(height * scale_ratio)
    # Resize image
    output_image = transposed_image.resize((resized_width, resized_height))
    # Create the target image and center the resized image
    resized_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
    left = (target_width - resized_width) // 2
    top = (target_height - resized_height) // 2
    resized_image.paste(output_image, (left, top))
    
    # The color quantization and dithering algorithms are performed, and the results are converted to RGB mode
    quantized_image = resized_image.quantize(dither=DISPLAY_DITHER, palette=PAL_IMAGE).convert('RGB')

    # Create a BytesIO object for image download
    byte_io = BytesIO()
    
    # Save the image to the BytesIO object
    quantized_image.save(byte_io, format="BMP") 
    
    # Get the bytes data
    byte_data = byte_io.getvalue()

    output_filename = os.path.splitext(uploaded_file.name)[0] + '_output.bmp'

    # Display columns
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Input: " + uploaded_file.name)
        st.image(input_image)
    
    with col2:
        st.header("Output: " + output_filename)
        st.image(quantized_image)

    with col3:
        st.download_button(
            label="Download photo",
            data=byte_data,
            file_name=output_filename
        )

    uploaded_file_path = pathlib.Path(temp_pic_dir) / output_filename
    st.write(uploaded_file_path)
    with open(uploaded_file_path, 'wb') as output_temporary_file:
        output_temporary_file.write(byte_data)

archive_file = None
with tempfile.TemporaryDirectory() as zip_dir:
    archive_file = shutil.make_archive(zip_dir + "/all", 'zip', temp_dir.name)
    st.write(archive_file)

    if os.path.exists(archive_file):
        with open(archive_file, 'rb') as archive_binary_file:
            st.download_button(
                label="Download all",
                data=archive_binary_file.read(),
                file_name="all.zip"
            )
    else:
        st.write("Upload one or more photos to get started!")

# Cleanup temporary directory
temp_dir.cleanup()