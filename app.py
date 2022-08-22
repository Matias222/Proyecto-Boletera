from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import zipfile
from bs4 import BeautifulSoup
import qrcode
from xml.dom.minidom import Document
from jinja2 import Template
import codecs


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

def texto(string):
    string=str(string)
    leer=0
    cadena=""
    for i in range(len(string)):
        if(leer==1): 
            if(string[i]=='<'): break
            cadena=cadena+string[i]
        if(string[i]=='>'): leer=1
    return cadena

def extraer_unidad(string):
    string=str(string)
    leer=0
    cadena='unitCode="'
    ans=""
    for i in string:
        if(leer>=10):
            if(i=='"'): break
            ans=ans+i
            leer=leer+1
        elif(i==cadena[leer]): leer=leer+1
    return ans

def lectura(path):

    with open(path, 'r') as f: data = f.read()

    Bs_data = BeautifulSoup(data, "xml")

    nombres=Bs_data.find_all('RegistrationName')
    nombre_negocio=texto(nombres[0])
    nombre_cliente=texto(nombres[1])

    direc_negocio=texto(Bs_data.find_all('Line')[0])

    info=Bs_data.find_all('ID')
    numero_boleta=texto(info[0])
    ruc_negocio=texto(info[2])
    documento_cliente=texto(info[3])

    descripcion_item=texto(Bs_data.find_all('Description')[0])

    hash=texto(Bs_data.find_all('DigestValue')[0])
    date=texto(Bs_data.find_all('IssueDate')[0])
    time=texto(Bs_data.find_all('IssueTime')[0])
    time=time[0:len(time)-4]
    precio_total = texto(Bs_data.find_all('PriceAmount')[0])
    monto_total_escrito=texto(Bs_data.find_all('Note')[0])

    impuesto=texto(Bs_data.find_all('TaxAmount')[0])
    cantidad=Bs_data.find_all('InvoicedQuantity')[0]
    unidad=extraer_unidad(cantidad)
    cantidad=texto(cantidad)

    telefono=952648192
    mail="plinioavendano@gmail.com"

    firmadigital=texto(Bs_data.find_all('SignatureValue'))
    digestvalue=texto(Bs_data.find_all('DigestValue'))

    print(firmadigital)

    print(nombre_negocio)
    print(nombre_cliente)
    print(direc_negocio)
    print(documento_cliente)
    print(ruc_negocio)
    print(numero_boleta)
    print(descripcion_item)
    print(date)
    print(time)
    print(hash)
    print(precio_total)
    print(monto_total_escrito)
    print(impuesto)
    print(cantidad)
    print(unidad)


    jinja2_template_string = open("templates/plantilla_2.html", 'rb').read()


    template = Template(jinja2_template_string.decode("utf-8"))


    html_template_string = template.render(nombre = nombre_negocio,ruc=ruc_negocio,direccion=direc_negocio,numero_boleta=numero_boleta,fecha=date,hora=time,cliente=nombre_cliente,documento=documento_cliente,descripcion=descripcion_item,total=precio_total,monto_total=precio_total,monto_total1=precio_total,son=monto_total_escrito,hash=hash)


    #print(html_template_string)

    file = codecs.open("templates/nuevo.html", "w", "utf-8")
    file.write(html_template_string)
    file.close()


    x = numero_boleta.split("-")

    if(len(documento_cliente)==8): tipodocumento='1'
    elif(len(documento_cliente)==11): tipodocumento='6'
    elif(len(documento_cliente)==12): tipodocumento='7'
    else: tipodocumento='-'

    #input_data = ruc_negocio+"|"+"03"+"|"+x[0]+"|"+x[1]+"|"+"0"+"|"+precio_total+"|"+date+"|"+str(tipodocumento)+"|"+documento_cliente+"|"+digestvalue+"|"+firmadigital
    input_data = ruc_negocio+"|"+"03"+"|"+x[0]+"|"+x[1]+"|"+"0"+"|"+precio_total+"|"+date+"|"+str(tipodocumento)+"|"+documento_cliente

    print(input_data)

    qr = qrcode.QRCode(
            version=2,
            box_size=10,
            border=5,  error_correction=qrcode.constants.ERROR_CORRECT_Q)

    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('static/images/qr.jpg')



@app.route('/', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        
        print(os.path.dirname(__file__))
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        
        with zipfile.ZipFile("static/files/"+file.filename,"r") as zip_ref:
            zip_ref.extractall("static/files/")
        

        lectura("static/files/"+file.filename[0:len(file.filename)-4]+".xml")

        return render_template("nuevo.html")

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
