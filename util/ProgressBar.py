# Print iterations progress
class ProgressBar:

    def __init__(self, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_progress_bar(0)

    def print_progress_bar(self, iteration):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(self.total)))
        filledLength = int(self.length * iteration // self.total)
        bar = self.fill * filledLength + '-' * (self.length - filledLength)
        print('\r%s |%s| %s%% %s' % (self.prefix, bar, percent, self.suffix), end = '\r')

        # Print New Line on Complete
        if iteration == self.total:
            print()

#
# Sample Usage
#

# from time import sleep
#
# # make a list
# items = list(range(0, 66))
# i = 0
# l = len(items)
#
# bar = ProgressBar(i, l, length = 30)
# # Initial call to print 0% progress
#
# for item in items:
#     # Do stuff...
#     sleep(0.1)
#     # Update Progress Bar
#     i += 1
#     bar.print_progress_bar(i)