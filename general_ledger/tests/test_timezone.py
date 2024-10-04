
# Importing the datetime module
import datetime

class TestTimeZone():

    def test_timezone_simple(self):
        # Storing the current date and time in
        # a new variable using the datetime.now()
        # function of datetime module
        current_date = datetime.datetime.now()

        # Checking the timezone information of the
        # object stored in tzinfo base class
        if current_date.tzinfo == None or current_date.tzinfo. \
                utcoffset(current_date) == None:

            # If passes the above condition then
            # the object is unaware
            print("Unaware")
        else:

            # Else printing "Aware"
            print("Aware")
