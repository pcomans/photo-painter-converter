import streamlit as st
import os.path
from io import BytesIO
from PIL import Image, ImagePalette, ImageOps

THUMBNAIL_SIZE = (400, 400) 

# Create a palette object
PAL_IMAGE = Image.new("P", (1,1))
PAL_IMAGE.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)

DISPLAY_DITHER = Image.Dither(Image.FLOYDSTEINBERG)
    

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

uploaded_files = st.file_uploader("Upload your photos", type=['png', 'jpg', 'gif', 'bmp', 'tiff'], accept_multiple_files=True)
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
            label="Download",
            data=byte_data,
            file_name=output_filename
        )