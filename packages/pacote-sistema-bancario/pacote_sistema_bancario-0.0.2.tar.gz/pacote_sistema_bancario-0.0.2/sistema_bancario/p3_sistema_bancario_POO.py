from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Usuario:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def nova_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Usuario):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, usuario):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._usuario = usuario
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, usuario, numero):
        return cls(numero, usuario)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def usuario(self):
        return self._usuario

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Operação não realizada. Saldo insuficiente.")
        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso.")
            return True
        else:
            print("Operação não realizada. Valor inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito realizado.")
        else:
            print("Operação não realizada. Valor inválido.")
            return False
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, usuario, limite=500, limite_saques=3):
        super().__init__(numero, usuario)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        num_saques = len([
            transacao for transacao in self.historico.transacoes
            if transacao["tipo"] == Saque.__name__
        ])

        if valor > self.saldo:
            print("Saque não realizado. Saldo insuficiente.")
        else:
            if valor > 0:
                if valor > self._limite:
                    print("O valor máximo por saque é de R$500,00. Tente novamente.")
                else:
                    num_saques += 1
                    if num_saques > self._limite_saques:
                        print("Saque não realizado: limite de saques diários atingidos.")
                    else:
                        return super().sacar(valor)
            else:
                print("Saque não realizado: valor inválido. Tente novamente")
        return False

    def __str__(self):
        return f"""\
Agência: {self.agencia}
Conta: {self.numero}
Responsável: {self.usuario.nome}
"""


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def nova_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%D-%m-%Y %H:%M:%S"),
        })


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.nova_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.nova_transacao(self)


def menu():
    menu = """

[d] Depositar
[s] Sacar
[e] Extrato
[n] Nova conta
[u] Novo usuário
[l] Mostrar contas
[q] Sair

=> """
    return input(menu)


def filtrar_usuario(cpf, usuarios):
    fil_usuario = [usuario for usuario in usuarios if usuario.cpf == cpf]
    if fil_usuario:
        return fil_usuario[0]
    else:
        return None


def recuperar_conta_usuario(usuario):
    if not usuario.contas:
        print("Usuário não possui conta.")
        return

    return usuario.contas[0]


def depositar(usuarios):
    cpf = input("CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Usuário não encontrado.")
        return

    valor = float(input("Valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    usuario.nova_transacao(conta, transacao)


def sacar(usuarios):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Usuário não encontrado.")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    usuario.nova_transacao(conta, transacao)


def exibir_extrato(usuarios):
    cpf = input("CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Usuário não encontrado.")
        return

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return

    print("Extrato ================================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"Saldo: R${conta.saldo:.2f}")
    print("==========================================")


def criar_usuario(usuarios):
    cpf = input("CPF (somente número): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("CPF já cadastrado.")
        return

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuario = PessoaFisica(
        nome=nome,
        data_nascimento=data_nascimento,
        cpf=cpf,
        endereco=endereco
    )

    usuarios.append(usuario)
    print("Usuário criado com sucesso.")


def criar_conta(numero_conta, usuarios, contas):
    cpf = input("CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Usuário não encontrado, tente novamente.")
        return

    conta = ContaCorrente.nova_conta(usuario=usuario, numero=numero_conta)
    contas.append(conta)
    usuario.contas.append(conta)

    print("Conta criada com sucesso.")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(str(conta))


def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(usuarios)

        elif opcao == "s":
            sacar(usuarios)

        elif opcao == "e":
            exibir_extrato(usuarios)

        elif opcao == "u":
            criar_usuario(usuarios)

        elif opcao == "n":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("Operação inválida, tente novamente.")

main()