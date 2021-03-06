from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from random import sample
from agents.places import Business, Base
from agents.rider import Moto, Van
from model.schedule import RandomActivationByType

class LastMileModel(Model):
        """A model with some number of Rider agents."""

        def __init__(self, N_moto, N_van, N_business, width, height):

                '''
                Add an Agent object to the schedule
                Args:
                    N_moto: Number of Motos
                    N_van: Number of Vans
                    N_businnes: Number of Business
                    width: grid width
                    height: grid length
                '''

                # Number of Motos
                self.n_motos = N_moto
                # Number of Vans
                self.n_vans = N_van
                # Number of destinies
                self.num_business = N_business
                # Grid Initializer
                self.grid = MultiGrid(width, height, False)
                # Time Module, in charge of runnning the agents
                self.schedule = RandomActivationByType(self)
                # Render Purposes
                self.running = True

                # Where the base and business are initialized
                self.base_location = self.get_random_positions(1)[0]

                positions = self.get_list_of_points_in_grid()
                positions.remove(self.base_location)
                self.business_locations = sample(positions, self.num_business)

                # Create Base
                self.base = self.add_base()

                # Create Business
                for loc in self.business_locations:
                        b = Business(loc, self)
                        self.schedule.add(b)
                        self.grid.place_agent(b, loc)

                # Create Agents
                for i in range(self.n_motos):
                        m = Moto(i, self)
                        self.schedule.add(m)

                        # Add riders to grid
                        self.grid.place_agent(m, self.base_location)

                # Create Agents
                for i in range(self.n_vans):
                        v = Van((self.n_motos + i), self)
                        self.schedule.add(v)

                        # Add riders to grid
                        self.grid.place_agent(v, self.base_location)

                # Add Datacollector
                self.datacollector = DataCollector(
                        {"Packs Moto": lambda m: m.schedule.get_pack_count_by_type(Moto),
                         "Packs Van": lambda m: m.schedule.get_pack_count_by_type(Van),
                         "Total Packs": lambda m: m.schedule.get_total_pack_count()
                        }
                )

                # Collect info at step 0
                self.datacollector.collect(self)

        def step(self):
                '''
                  Performs step on all Agents
                '''

                self.datacollector.collect(self)
                self.schedule.step()

        def add_base(self):
                '''
                  Adds Delivery Headquarter
                Returns Head Quarter Agent Object
                '''
                base = Base(self.base_location, self)
                self.grid.place_agent(base, self.base_location)
                self.schedule.add(base)
                return base

        def get_list_of_points_in_grid(self):

                '''
                Returns list of grid coordinates
                '''

                grid_points = []
                for agents, x, y in self.grid.coord_iter():
                        grid_points.append((x, y))

                return grid_points

        def get_random_positions(self, N=1):

                '''
                Returns list of N random coordinates in grid
                '''

                positions = self.get_list_of_points_in_grid()

                return sample(positions, N)
