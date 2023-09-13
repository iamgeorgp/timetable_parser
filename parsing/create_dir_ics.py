'''
Script to renew .ics files
'''

import pars_all_g
# Cleaning folders with .ucs
pars_all_g.del_all_ics('current_week')
pars_all_g.del_all_ics('next_week')
# Pars new schedules
pars_all_g.pars_ics_for_db()