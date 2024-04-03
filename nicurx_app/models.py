from django.db import models

# Create your models here.
class Medication(models.Model):

    #List of choices for major value in database, human readable name
    CalculationUnit = (
    ('KG', 'Kilograms'),
    ('BSA', 'Body Mass Index'),
    ('None', 'None'),
    )
    medication_name = models.CharField(max_length=200)
    email = models.CharField("UCCS Email", max_length=200)
    calculation_unit = models.CharField(max_length=200, choices=CalculationUnit, blank = False)

    #Define default String to return the name for representing the Model object."
    def __str__(self):
        return self.name
    
    #Returns the URL to access a particular instance of MyModelName.
    #if you define this method then Django will automatically
    # add a "View on Site" button to the model's record editing screens in the Admin site
    def get_absolute_url(self):
        return reverse('student-detail', args=[str(self.id)])