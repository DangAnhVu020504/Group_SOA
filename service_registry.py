import consul
import os


class ServiceRegistry:
	"""Simple Consul registration helper.

	- Registers the service under the provided name and port.
	- Registers the address `127.0.0.1` by default (override via SERVICE_REGISTRY_ADDRESS).
	- Provides a deregister method to be called on shutdown.
	"""

	def __init__(self, service_name, service_port, consul_host="localhost", consul_port=8500):
		self.consul_client = consul.Consul(host=consul_host, port=consul_port)
		self.service_name = service_name
		self.service_port = service_port
		self.service_id = f"{service_name}-{service_port}"
		# Address to register in Consul (default to localhost)
		self.address = os.environ.get("SERVICE_REGISTRY_ADDRESS", "127.0.0.1")

	def register(self):
		try:
			self.consul_client.agent.service.register(
				name=self.service_name,
				service_id=self.service_id,
				address=self.address,
				port=self.service_port,
			)
			print(f"Successfully registered service {self.service_name} ({self.address}:{self.service_port}) with Consul")
		except Exception as e:
			print(f"Failed to register service with Consul: {str(e)}")

	def deregister(self):
		try:
			self.consul_client.agent.service.deregister(self.service_id)
			print(f"Successfully deregistered service {self.service_name} from Consul")
		except Exception as e:
			print(f"Failed to deregister service from Consul: {str(e)}")

