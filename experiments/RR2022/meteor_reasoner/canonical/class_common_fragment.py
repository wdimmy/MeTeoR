class CommonFragment:
    def __init__(self, base_interval, cr_flag=True):
        """
        Args:
            base_interval: [t_D^-, t_D^+]
            common:
            cr_flag:
        """
        self.base_interval = base_interval
        self.common = None
        self.cr_flag = cr_flag